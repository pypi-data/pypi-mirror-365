import abc
import collections
import functools
import hashlib
import pathlib
from typing import Tuple
import warnings

import h5py
import numpy as np


class EmptyDatasetWarning(UserWarning):
    """Used for files that contain no actual data"""
    pass


class BaseImageChunkCache(abc.ABC):
    def __init__(self,
                 shape: Tuple[int],
                 chunk_size: int = 1000,
                 cache_size: int = 2,
                 ):
        self.shape = shape
        self._dtype = None
        chunk_size = min(shape[0], chunk_size)
        self._len = self.shape[0]

        self.cache = collections.OrderedDict()
        """This is a FILO cache for the chunks"""

        self.image_shape = self.shape[1:]
        self.chunk_shape = (chunk_size,) + self.shape[1:]
        self.chunk_size = chunk_size
        self.cache_size = cache_size
        self.num_chunks = int(np.ceil(self._len / (self.chunk_size or 1)))

    def __getitem__(self, index):
        if isinstance(index, (slice, list, np.ndarray)):
            if isinstance(index, slice):
                indices = np.arange(
                    index.start or 0,
                    min(index.stop, len(self)) if index.stop else len(self),
                    index.step)
            else:
                indices = index
            array_out = np.empty((len(indices),) + self.image_shape,
                                 dtype=self.dtype)
            for ii, idx in enumerate(indices):
                array_out[ii] = self[idx]
            return array_out
        else:
            chunk_index, sub_index = self._get_chunk_index_for_index(index)
            return self.get_chunk(chunk_index)[sub_index]

    def __len__(self):
        return self._len

    @property
    def dtype(self):
        """data type of the image data"""
        if self._dtype is None:
            self._dtype = self[0].dtype
        return self._dtype

    @abc.abstractmethod
    def _get_chunk_data(self, chunk_slice):
        """Implemented in subclass to obtain actual data"""

    def _get_chunk_index_for_index(self, index):
        if index < 0:
            index = self._len + index
        elif index >= self._len:
            raise IndexError(
                f"Index {index} out of bounds for HDF5ImageCache "
                f"of size {self._len}")
        index = int(index)  # convert np.uint64 to int, so we get ints below
        chunk_index = index // self.chunk_size
        sub_index = index % self.chunk_size
        return chunk_index, sub_index

    def get_chunk(self, chunk_index):
        """Return one chunk of images"""
        if chunk_index not in self.cache:
            if len(self.cache) >= self.cache_size:
                # Remove the first item
                self.cache.popitem(last=False)
            data = self._get_chunk_data(self.get_chunk_slice(chunk_index))
            self.cache[chunk_index] = data
        return self.cache[chunk_index]

    def get_chunk_size(self, chunk_index):
        """Return the number of images in this chunk"""
        if chunk_index < self.num_chunks - 1:
            return self.chunk_size
        else:
            chunk_size = self._len - chunk_index*self.chunk_size
            if chunk_size < 0:
                raise IndexError(f"{self} only has {self.num_chunks} chunks!")
            return chunk_size

    def get_chunk_slice(self, chunk_index):
        """Return the slice corresponding to the chunk index"""
        ch_slice = slice(self.chunk_size * chunk_index,
                         self.chunk_size * (chunk_index + 1)
                         )
        return ch_slice

    def iter_chunks(self):
        index = 0
        chunk = 0
        while True:
            yield chunk
            chunk += 1
            index += self.chunk_size
            if index >= self._len:
                break


class HDF5ImageCache(BaseImageChunkCache):
    def __init__(self,
                 h5ds: h5py.Dataset,
                 chunk_size: int = 1000,
                 cache_size: int = 2,
                 boolean: bool = False):
        """An HDF5 image cache

        Deformability cytometry data files commonly contain image stacks
        that are chunked in various ways. Loading just a single image
        can be time-consuming, because an entire HDF5 chunk has to be
        loaded, decompressed and from that one image extracted. The
        `HDF5ImageCache` class caches the chunks from the HDF5 files
        into memory, making single-image-access very fast.
        """
        super(HDF5ImageCache, self).__init__(
            shape=h5ds.shape,
            chunk_size=chunk_size,
            cache_size=cache_size)
        # TODO:
        # - adjust chunking to multiples of the chunks in the dataset
        #   (which might slightly speed up things)
        self.h5ds = h5ds
        self.boolean = boolean

        if self._len == 0:
            warnings.warn(f"Input image '{h5ds.name}' in "
                          f"file {h5ds.file.filename} has zero length",
                          EmptyDatasetWarning)

    def _get_chunk_data(self, chunk_slice):
        data = self.h5ds[chunk_slice]
        if self.boolean:
            data = np.array(data, dtype=bool)
        return data


class ImageCorrCache(BaseImageChunkCache):
    def __init__(self,
                 image: HDF5ImageCache,
                 image_bg: HDF5ImageCache):
        super(ImageCorrCache, self).__init__(
            shape=image.shape,
            chunk_size=image.chunk_size,
            cache_size=image.cache_size)
        self.image = image
        self.image_bg = image_bg

    def _get_chunk_data(self, chunk_slice):
        data = np.array(
            self.image._get_chunk_data(chunk_slice), dtype=np.int16) \
           - self.image_bg._get_chunk_data(chunk_slice)
        return data


@functools.cache
def md5sum(path, blocksize=65536, count=0):
    """Compute (partial) MD5 sum of a file

    Parameters
    ----------
    path: str or pathlib.Path
        path to the file
    blocksize: int
        block size in bytes read from the file
        (set to `0` to hash the entire file)
    count: int
        number of blocks read from the file
    """
    path = pathlib.Path(path)

    hasher = hashlib.md5()
    with path.open('rb') as fd:
        ii = 0
        while len(buf := fd.read(blocksize)) > 0:
            hasher.update(buf)
            ii += 1
            if count and ii == count:
                break
    return hasher.hexdigest()
