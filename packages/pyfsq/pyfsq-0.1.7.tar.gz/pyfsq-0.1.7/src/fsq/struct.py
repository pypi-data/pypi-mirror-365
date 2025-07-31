"""FSQ structs and protocol constants."""

from dataclasses import dataclass, field
from typing import Union
from enum import IntEnum, IntFlag
from .strenum_compat import StrEnum

FSQ_PROTOCOL_VERSION = 1
FSQ_PACKET_LENGTH    = 6424

# String length constants defined in FSQ C project.
DSM_MAX_NODE_LENGTH     = 64    # Maximum length that is permitted for node name.
DSM_MAX_VERIFIER_LENGTH = 64    # Maximum length that is permitted for node password.
DSM_MAX_FSNAME_LENGTH   = 1024  # Maximum length that is permitted for filespace.
DSM_MAX_DESCR_LENGTH    = 255   # Maximum length that is permitted for description.
FSQ_MAX_ERRMSG_LENGTH   = 1024  # Maximum length that is permitted for fsq error message.
HOST_NAME_MAX           = 64    # Maximum length that is permitted for hostname.
PATH_MAX                = 4096  # Maximum length that is permitted for file path.

class PackUnpackFormat(StrEnum):
    """Formats for packing and unpacking FSQ structs."""
    CONNECT    = '=Bi1025sxxxi65s65s65sxi5187x'
    OPEN       = '=Bi1025sxxxi1025s4097s256s2xixxx'
    DATA       = '=Bi1025sxxxiQ5379x'
    CLOSE      = '=Bi1025sxxxi5387x'
    DISCONNECT = '=Bi1025sxxxi5387x'

class FsqProtocolState(IntFlag):
    """FSQ protocol states."""
    FSQ_CONNECT    = 0x1
    FSQ_OPEN       = 0x2
    FSQ_DATA       = 0x4
    FSQ_CLOSE      = 0x8
    FSQ_DISCONNECT = 0x10
    FSQ_REPLY      = 0x20
    FSQ_ERROR      = 0x40

class FsqStorageDest(IntEnum):
    """FSQ destination storage targets."""
    FSQ_STORAGE_NULL       = 0
    FSQ_STORAGE_LOCAL      = 1
    FSQ_STORAGE_LUSTRE     = 2
    FSQ_STORAGE_TSM        = 3
    FSQ_STORAGE_LUSTRE_TSM = 4

class FsqProtocolError(Exception):
    """Exception class reporting FSQ protocotol specific errors."""

class FsqServerError(Exception):
    """Exception class reporting FSQ server specific errors."""

@dataclass
class FsqLogin:
    """FSQ login class required in connect(...) call."""
    node: bytes = bytes(DSM_MAX_NODE_LENGTH + 1)
    password: bytes = bytes(DSM_MAX_VERIFIER_LENGTH + 1)
    hostname: bytes = bytes(HOST_NAME_MAX + 1)
    port: int = 0

@dataclass
class FsqInfo:
    """FSQ info class required in open(...) call."""
    fs: bytes = bytes(DSM_MAX_FSNAME_LENGTH + 1)
    fpath: bytes = bytes(PATH_MAX + 1)
    desc: bytes = bytes(DSM_MAX_DESCR_LENGTH + 1)
    fsq_storage_dest: FsqStorageDest = FsqStorageDest.FSQ_STORAGE_NULL

@dataclass
class FsqData:
    """FSQ data class required in write(...) call."""
    size: int = 0

@dataclass
class FsqError:
    """FSQ error class comprising possible errors occured on FSQ server."""
    rc: int = 0
    strerror: bytes = bytes(FSQ_MAX_ERRMSG_LENGTH + 1)

@dataclass
class FsqPacket:
    """FSQ packet class transferred in FSQ protocol."""
    ver: int = 0
    error: FsqError = field(default_factory=FsqError)
    state: FsqProtocolState = FsqProtocolState.FSQ_CONNECT
    data: Union[FsqLogin, FsqInfo, FsqData] = field(default_factory=FsqLogin)
