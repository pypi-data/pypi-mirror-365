"""FSQ context manager API for writing data to FSQ server."""

from .api import Api
from .struct import FsqStorageDest

class Connect:
    """FSQ context manager class providing connection to FSQ server."""

    def __init__(self, node: str, password: str, hostname: str, port: int) -> None:
        self.node = node
        self.password = password
        self.hostname = hostname
        self.port = port
        self.fsq = Api()

    def __enter__(self) -> Api:
        self.fsq.connect(self.node, self.password, self.hostname, self.port)
        return self.fsq

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.fsq.disconnect()

class Open:
    """FSQ context manager class providing data open and data write to FSQ server."""

    def __init__(self, fsq: Api, fs: str, fpath: str, desc: str, dest: FsqStorageDest) -> None:
        self.fsq = fsq
        self.fs = fs
        self.fpath = fpath
        self.desc = desc
        self.dest = dest

    def __enter__(self) -> None:
        self.fsq.open(self.fs, self.fpath, self.desc, self.dest)

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.fsq.close()
