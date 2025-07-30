import warnings
from enum import Enum
from multiprocessing import shared_memory
from .namedLock import NamedLock

class BlockSize(Enum):
    s64 = 64
    s128 = 128
    s256 = 256
    s512 = 512
    s1024 = 1024

class RememoryString:
    """
    A fixed-size shared string.
    The memory block stores a UTF-8 encoded string up to max_size bytes.
    Strings longer than max_size will be truncated (with a warning).
    """

    def __init__(self, name: str, size: BlockSize = BlockSize.s256):
        """
        :param name: Shared memory block name
        :param size: StringSizes enum value (buffer size)
        """
        self._name = name
        self._max_size = size.value
        self._shm = None

        try:
            self._shm = shared_memory.SharedMemory(name=name)
        except FileNotFoundError:
            self._shm = shared_memory.SharedMemory(
                name=name, create=True, size=self._max_size
            )
            self._write_value("")

        self._lock = NamedLock(name)

    def _read_value(self) -> str:
        if self._shm is None:
            return ""
        raw = bytes(self._shm.buf[:self._max_size])
        return raw.rstrip(b"\x00").decode("utf-8")

    def _write_value(self, value: str):
        if self._shm is None:
            return
        data = value.encode("utf-8")
        if len(data) > self._max_size:
            warnings.warn(
                f"RememoryString[{self._name}] value too long "
                f"({len(data)} > {self._max_size}), truncating."
            )
            data = data[:self._max_size]
        # write and zero-fill
        self._shm.buf[:len(data)] = data
        self._shm.buf[len(data):self._max_size] = b"\x00" * (self._max_size - len(data))

    @property
    def value(self) -> str:
        with self._lock:
            return self._read_value()

    @value.setter
    def value(self, new_value: str):
        with self._lock:
            self._write_value(new_value)

    def set(self, new_value: str):
        self.value = new_value

    def get(self) -> str:
        return self.value

    def __str__(self) -> str:
        return self.value

    def __repr__(self):
        return f"<RememoryString {self._name}: '{self._read_value()}'>"

    def close(self):
        if self._shm is not None:
            self._shm.close()

    def unlink(self):
        if self._shm is not None:
            self._shm.unlink()
