import queue
import time

import numpy as np
from scipy import ndimage

from ...read import HDF5Data

from ...os_env_st import RequestSingleThreaded, confirm_single_threaded

from .base import mp_spawn, Background


class BackgroundSparseMed(Background):
    def __init__(self, input_data, output_path, kernel_size=200,
                 split_time=1., thresh_cleansing=0, frac_cleansing=.8,
                 offset_correction=True,
                 compress=True,
                 num_cpus=None):
        """Sparse median background correction with cleansing

        In contrast to the rolling median background correction,
        this algorithm only computes the background image every
        ``split_time`` seconds, but with a larger window (default kernel
        size is 200 frames instead of 100 frames).

        1. At time stamps every `split_time` seconds, a background image is
           computed, resulting in a background series.
        2. Cleansing: The background series is checked for images that
           contain event data using a lengthy algorithm that is documented
           in the source code (sorry). In short, this gets rid of
           background images that contain streaks of RBCs.
        3. Each frame gets the background image closest to it
           based on time from the background series.

        Parameters
        ----------
        input_data: array-like or pathlib.Path
            The input data can be either a path to an HDF5 file with
            the "evtens/image" dataset or an array-like object that
            behaves like an image stack (first axis enumerates events).
        output_path: pathlib.Path
            Path to the output file. If `input_data` is a path, you can
            set `output_path` to the same path to write directly to the
            input file. The data are written in the "events/image_bg"
            dataset in the output file.
        kernel_size: int
            Kernel size for median computation. This is the number of
            events that are used to compute the median for each pixel.
        split_time: float
            Time between background images in the background series
        thresh_cleansing: float
            A positive floating point value for scaling the thresholding
            operation when excluding background images from the series.
            Larger values mean more background images are excluded.
            Set to zero to enforce a fixed fraction via `frac_cleansing`.
        frac_cleansing: float
            Fraction between 0 and 1 indicating how many background images
            must still be present after cleansing (in case the cleansing
            factor is too large). Set to 1 to disable cleansing altogether.
        offset_correction: bool
            The sparse median background correction produces one median
            image for multiple input frames (BTW this also leads to very
            efficient data storage with internal HDF5 basins). In
            case the input frames are subject to frame-by-frame brightness
            variations (e.g. flickering of the illumination source), it
            is useful to have an offset value per frame that can then be
            used in a later step to perform a more accurate background
            correction. This offset is computed here by taking a 20px wide
            slice from each frame (where the channel wall is located)
            and computing the median therein relative to the computed
            background image. The data are written to the "bg_off" feature
            in the output file alongside "image_bg". To obtain the
            corrected background image, add "image_bg" and "bg_off".
            Set this to False if you don't need the "bg_off" feature.
        compress: bool
            Whether to compress background data. Set this to False
            for faster processing.
        num_cpus: int
            Number of CPUs to use for median computation. Defaults to
            `multiprocessing.cpu_count()`.

        .. versionchanged:: 0.23.5

            The background image data are stored as an internal
            mapped basin to reduce the output file size.
        """
        super(BackgroundSparseMed, self).__init__(
            input_data=input_data,
            output_path=output_path,
            compress=compress,
            num_cpus=num_cpus,
            kernel_size=kernel_size,
            split_time=split_time,
            thresh_cleansing=thresh_cleansing,
            frac_cleansing=frac_cleansing,
            offset_correction=offset_correction,
        )

        if kernel_size > len(self.input_data):
            self.logger.warning(
                f"The kernel size {kernel_size} is too large for input data"
                f"size {len(self.input_data)}. Setting it to input data size!")
            kernel_size = len(self.input_data)

        self.kernel_size = kernel_size
        """kernel size used for median filtering"""

        self.split_time = split_time
        """time between background images in the background series"""

        self.thresh_cleansing = thresh_cleansing
        """cleansing threshold factor"""

        self.frac_cleansing = frac_cleansing
        """keep at least this many background images from the series"""

        self.offset_correction = offset_correction
        """offset/flickering correction"""

        # time axis
        self.time = None
        if self.h5in is not None:
            hd = HDF5Data(self.h5in)
            if "time" in hd:
                # use actual time from dataset
                self.time = hd["time"][:]
                self.time -= self.time[0]
            elif "imaging:frame rate" in hd.meta:
                fr = hd.meta["imaging:frame rate"]
                if "frame" in hd:
                    # compute time from frame rate and frame numbers
                    self.time = hd["frame"] / fr
                    self.time -= self.time[0]
                else:
                    # compute time using frame rate (approximate)
                    dur = self.image_count / fr * 1.5
                    self.logger.info(
                        f"Approximating duration: {dur/60:.1f}min")
                    self.time = np.linspace(0, dur, self.image_count,
                                            endpoint=True)
        if self.time is None:
            # No HDF5 file or no information therein; Make an educated guess.
            dur = self.image_count / 3600 * 1.5
            self.logger.info(f"Guessing duration: {dur/60:.1f}min")
            self.time = np.linspace(0, dur, self.image_count,
                                    endpoint=True)

        self.duration = self.time[-1] - self.time[0]
        """duration of the measurement"""

        self.step_times = np.arange(0, self.duration, self.split_time)

        self.bg_images = np.zeros((self.step_times.size,
                                   self.image_shape[0],
                                   self.image_shape[1]),
                                  dtype=np.uint8)
        """array containing all background images"""

        self.shared_input_raw = mp_spawn.RawArray(
            np.ctypeslib.ctypes.c_uint8,
            int(np.prod(self.image_shape)) * kernel_size)
        """mp.RawArray for temporary batch input data"""

        self.shared_output_raw = mp_spawn.RawArray(
            np.ctypeslib.ctypes.c_uint8,
            int(np.prod(self.image_shape)))
        """mp.RawArray for the median background image"""

        # Convert the RawArray to something we can write to fast
        # (similar to memoryview, but without having to cast) using
        # np.ctypeslib.as_array. See discussion in
        # https://stackoverflow.com/questions/37705974
        self.shared_input = np.ctypeslib.as_array(
            self.shared_input_raw).reshape(kernel_size, -1)
        """numpy array reshaped view on `self.shared_input_raw`.
        The First axis enumerating the events
        """

        self.shared_output = np.ctypeslib.as_array(
            self.shared_output_raw).reshape(self.image_shape)
        """numpy array reshaped view on `self.shared_output_raw`.
        The First axis enumerating the events
        """

        self.pool = mp_spawn.Pool(processes=self.num_cpus)
        """multiprocessing pool for parallel processing"""

        self.worker_counter = mp_spawn.Value("l", 0)
        """counter tracking process of workers"""

        self.queue = mp_spawn.Queue()
        """queue for median computation jobs"""

        self.workers = [WorkerSparseMed(self.queue,
                                        self.worker_counter,
                                        self.shared_input_raw,
                                        self.shared_output_raw,
                                        self.kernel_size)
                        for _ in range(self.num_cpus)]
        """list of workers (processes)"""
        [w.start() for w in self.workers]

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.worker_counter.value = -1000
        [w.join() for w in self.workers]
        self.pool.terminate()
        self.pool.join()
        super(BackgroundSparseMed, self).__exit__(type, value, tb)

    @staticmethod
    def check_user_kwargs(*,
                          kernel_size: int = 200,
                          split_time: float = 1.,
                          thresh_cleansing: float = 0,
                          frac_cleansing: float = .8,
                          offset_correction: bool = True,
                          ):
        """Initialize user-defined properties of this class

        This method primarily exists so that the CLI knows which
        keyword arguments can be passed to this class.

        Parameters
        ----------
        kernel_size: int
            Kernel size for median computation. This is the number of
            events that are used to compute the median for each pixel.
        split_time: float
            Time between background images in the background series
        thresh_cleansing: float
            A positive floating point value for scaling the thresholding
            operation when excluding background images from the series.
            Larger values mean more background images are excluded.
            Set to 0 (default) to enforce a fixed fraction `frac_cleansing`.
        frac_cleansing: float
            Fraction between 0 and 1 indicating how many background images
            must still be present after cleansing (in case the cleansing
            factor is too large). Set to 1 to disable cleansing altogether.
        offset_correction: bool
            The sparse median background correction produces one median
            image for multiple input frames (BTW this also leads to very
            efficient data storage with internal HDF5 basins). In
            case the input frames are subject to frame-by-frame brightness
            variations (e.g. flickering of the illumination source), it
            is useful to have an offset value per frame that can then be
            used in a later step to perform a more accurate background
            correction. This offset is computed here by taking a 20px wide
            slice from each frame (where the channel wall is located)
            and computing the median therein relative to the computed
            background image. The data are written to the "bg_off" feature
            in the output file alongside "image_bg". To obtain the
            corrected background image, add "image_bg" and "bg_off".
            Set this to False if you don't need the "bg_off" feature.
        """
        assert kernel_size > 0
        assert split_time > 0
        assert thresh_cleansing >= 0, "Cleansing threshold must be >=0"
        assert frac_cleansing > 0, "Cleansing fraction must be >0"
        assert frac_cleansing <= 1, "Cleansing fraction must be <=1"

    def process_approach(self):
        """Perform median computation on entire input data"""

        # Compute initial background images (populates self.bg_images)
        for ii, ti in enumerate(self.step_times):
            self.process_second(ii, ti)

        if self.frac_cleansing != 1:
            # The following algorithm finds background images that contain
            # event information (this happens when the median background step
            # gets input images where at a certain position there are mostly
            # cells, i.e. there are too many cells in all images). Ideally,
            # background images don't contain event information. Normally,
            # the events are red blood cells which are dark and have a strong
            # effect.
            # For each of those images, compute the ptp profile (ptp along the
            # channel axis)
            bg_prof = np.ptp(self.bg_images, axis=2)
            # compute the median of those profiles along the channel axis
            bg_prof_med = np.median(bg_prof, axis=0)
            # normalize the profiles
            bg_prof_norm = bg_prof - bg_prof_med.reshape(1, -1)
            # compute the mean at the center for each profile;
            width = bg_prof.shape[1]
            spread = max(20, width // 4)
            cslice = slice(width // 2 - spread, width // 2 + spread)
            # If you plot this line, you will already see outliers (e.g. use
            # the leukocytes.rtdc reference measurement).
            bg_prof_norm_cent = np.mean(bg_prof_norm[:, cslice], axis=1)
            # To reliably remove outliers, we still need a constant baseline
            # which we achieve by computing the median filter. The size
            # of 10 is just a best-guess and makes sense since it's time-based
            # and not frame-based. This would most-likely not work if you
            # applied this in `BackgroundRollMed`.
            bg_profiles_norm_cent_med = ndimage.median_filter(
                bg_prof_norm_cent, size=10)
            # Until now, we are basically looking at the peak-to-peak grayscale
            # values from which a median was subtracted.
            x = bg_prof_norm_cent - bg_profiles_norm_cent_med

            ref = np.abs(x - np.median(x))
            thresh_fact = np.var(ref) * 150
            if self.thresh_cleansing != 0:
                # Try a simple thresholding approach.
                thresh = thresh_fact / self.thresh_cleansing
            else:
                # Force a certain quantile fraction to be removed
                thresh = np.quantile(ref, self.frac_cleansing)
            used = ref <= thresh
            frac_remove = np.sum(~used) / used.size

            # Check whether we can trust the current selection
            if (self.thresh_cleansing != 0
                    and (1 - frac_remove) < self.frac_cleansing):
                # This did not work at all.
                # use quantiles instead
                frac_remove_user = frac_remove
                thresh = np.quantile(ref, self.frac_cleansing)
                used = ref <= thresh
                frac_remove = np.sum(~used) / used.size
                self.logger.warning(
                    f"{frac_remove_user:.1%} of the background images would "
                    f"be removed with the current settings, so we enforce "
                    f"`frac_cleansing`. To avoid this warning, try decreasing "
                    f"`thresh_cleansing` or `frac_cleansing`. The new "
                    f"threshold is {thresh_fact / thresh}.")

            self.logger.info(f"Cleansed {frac_remove:.2%}")
            step_times = self.step_times[used]
            bg_images = self.bg_images[used]
        else:
            self.logger.info("Background series cleansing disabled")
            step_times = self.step_times
            bg_images = self.bg_images

        # Assign each frame to a certain background index
        bg_idx = np.zeros(self.image_count, dtype=int)
        idx0 = 0
        idx1 = None
        for ii in range(len(step_times)):
            t1 = step_times[ii]
            idx1 = np.argmin(np.abs(self.time - t1 - self.split_time/2))
            bg_idx[idx0:idx1] = ii
            idx0 = idx1
        if idx1 is not None:
            # Fill up remainder of index array with last entry
            bg_idx[idx1:] = ii

        # Store the background images as an internal mapped basin
        self.writer.store_basin(
            name="background images",
            description=f"Pipeline identifier: {self.get_ppid()}",
            mapping=bg_idx,
            internal_data={"image_bg": bg_images}
            )

        # store the offset correction, if applicable
        if self.offset_correction:
            self.logger.info("Computing offset correction")
            # compute the mean at the top of all background images
            sh, sw = self.input_data.shape[1:]
            roi_full = (slice(None), slice(0, 20), slice(0, sw))
            bg_data_mean = np.mean(bg_images[roi_full], axis=(1, 2))
            pos = 0
            step = self.writer.get_best_nd_chunks(item_shape=(sh, sw),
                                                  feat_dtype=np.uint8)[0]
            bg_off = np.zeros(self.image_count, dtype=float)
            # For every chunk in the input image data, compute that
            # value as well and store the resulting offset value.
            # TODO: Could this be parallelized, or are we limited in reading?
            while pos < self.image_count:
                stop = min(pos + step, self.image_count)
                # Record background offset correction "bg_off". We take a
                # slice of 20px from the top of the image (there are normally
                # no events here, only the channel walls are visible).
                cur_slice = slice(pos, stop)
                # mean background brightness
                val_bg = bg_data_mean[bg_idx[cur_slice]]
                # mean image brightness
                roi_cur = (cur_slice, slice(0, 20), slice(0, sw))
                val_dat = np.mean(self.input_data[roi_cur], axis=(1, 2))
                # background image = image_bg + bg_off
                bg_off[cur_slice] = val_dat - val_bg
                # set progress
                self.image_proc.value = 0.5 * (1 + pos / self.image_count)
                pos = stop
            # finally, store the background offset feature
            self.writer.store_feature_chunk("bg_off", bg_off)

        self.image_proc.value = 1

    def process_second(self,
                       ii: int,
                       second: float | int):
        idx_start = np.argmin(np.abs(second - self.time))
        idx_stop = idx_start + self.kernel_size
        if idx_stop >= self.image_count:
            idx_stop = self.image_count
            idx_start = max(0, idx_stop - self.kernel_size)
        assert idx_stop - idx_start == self.kernel_size

        # The following is equivalent to, but faster than:
        # self.bg_images[ii] = np.median(self.input_data[idx_start:idx_stop],
        #                                axis=0)

        self.worker_counter.value = 0
        self.shared_input[:] = self.input_data[idx_start:idx_stop].reshape(
            self.kernel_size, -1)

        self.worker_counter.value = 0

        num_jobs = 0
        # Cut the image into jobs with ival=500 pixels which seems
        # optimal on Paul's laptop.
        height, width = self.image_shape
        start = 0
        ival = 500
        smax = height * width
        while start < smax:
            args = (slice(start, start+ival),)
            start += ival
            self.queue.put(args)
            num_jobs += 1

        # block until workers are done
        while True:
            time.sleep(.01)
            if self.worker_counter.value == num_jobs:
                break

        self.bg_images[ii] = self.shared_output.reshape(self.image_shape)

        self.image_proc.value = idx_stop / (
                # with offset correction, everything is slower
                self.image_count * (1 + self.offset_correction))


class WorkerSparseMed(mp_spawn.Process):
    def __init__(self, job_queue, counter, shared_input, shared_output,
                 kernel_size, *args, **kwargs):
        """Worker process for median computation"""
        super(WorkerSparseMed, self).__init__(*args, **kwargs)
        self.queue = job_queue
        self.queue.cancel_join_thread()
        self.counter = counter
        self.shared_input_raw = shared_input
        self.shared_output_raw = shared_output
        self.kernel_size = kernel_size

    def run(self):
        """Main loop of worker process (breaks when `self.counter` <0)"""
        # confirm single-threadedness (prints to log)
        confirm_single_threaded()
        # Create the ctypes arrays here instead of during __init__, because
        # for some reason they are copied in __init__ and not mapped.
        shared_input = np.ctypeslib.as_array(
            self.shared_input_raw).reshape(self.kernel_size, -1)
        shared_output = np.ctypeslib.as_array(self.shared_output_raw)
        while True:
            if self.counter.value < 0:
                break
            try:
                args = self.queue.get(timeout=.1)
            except queue.Empty:
                pass
            else:
                job_slice = args[0]
                # Compute the median of a subslice of the array.
                # Use np.partition which has less overhead than np.median
                # (code copy-pasted from np.median):
                kth = shared_input.shape[0] // 2
                part = np.partition(a=shared_input[:, job_slice],
                                    kth=kth,
                                    axis=0)
                # Note that we only partition at `kth`, regardless of the
                # input size. This is ok, because we are only interested
                # in integers anyway and +/- one grayscale value does not
                # really matter.
                shared_output[job_slice] = part[kth]
                # shared_output[job_slice] = np.median(
                #     shared_input[:, job_slice],
                #     axis=0,
                #     overwrite_input=False)
                with self.counter.get_lock():
                    self.counter.value += 1

    def start(self):
        # Set all relevant os environment variables such libraries in the
        # new process only use single-threaded computation.
        with RequestSingleThreaded():
            mp_spawn.Process.start(self)
