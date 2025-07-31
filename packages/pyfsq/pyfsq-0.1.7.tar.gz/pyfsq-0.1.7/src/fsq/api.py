"""FSQ API for writing data to FSQ server."""

import os
import logging
import socket
import struct
from .struct import FsqPacket, FsqData, FsqError, FsqInfo, FsqLogin, FsqStorageDest
from .struct import FsqProtocolError, FsqServerError, FsqProtocolState
from .struct import PackUnpackFormat, FSQ_PROTOCOL_VERSION, FSQ_PACKET_LENGTH

class Api:
    """FSQ API class providing methods for transfering data to FSQ server."""

    def __init__(self) -> None:
        self.fsq_packet = FsqPacket(ver=FSQ_PROTOCOL_VERSION,
                                    error=FsqError(rc=0, strerror=b''))
        self.sock: socket.socket
        self.fpath_logging = None
        self.hostname_logging = None

    def __verify_fsq_packet(self, data: tuple, state: FsqProtocolState) -> None:

        fsq_packet = FsqPacket(ver=data[0],
                               error=FsqError(rc=data[1],
                                              strerror=data[2].decode('ascii').strip('\x00')),
                               state=data[3])

        if fsq_packet.ver != FSQ_PROTOCOL_VERSION:
            raise FsqProtocolError(f'protocol error: unsupported FSQ protocol '
                                   f'version {fsq_packet.ver}, '
                                   f'required version is {FSQ_PROTOCOL_VERSION}')

        if fsq_packet.error.rc != 0:
            raise FsqServerError(f'server error '
                                 f'{fsq_packet.error.rc}:{fsq_packet.error.strerror}'
                                 f':\'{os.strerror(abs(fsq_packet.error.rc))}\'')

        if fsq_packet.state != state:
            raise FsqProtocolError(f'protocol error: received state {hex(fsq_packet.state)}, '
                                   f'expected state {hex(state)}')

    def connect(self, node: str, password: str, hostname: str, port: int) -> None:
        """Connect to FSQ server.

        Connect via TCP socket to FSQ server. On the FSQ server side, the
        arguments node and password are sent to a TSM server for authentication.
        If the TSM server authentication fails, then the result and error is transmitted
        to the client and the socket is closed.

        Parameters
        ----------
        node : str
            Node name.
        password : str
            Node password.
        hostname : str
            Hostname or IP address of the FSQ server.
        port : int
            TCP port of the FSQ server.

        Examples
        --------
        connect('tsmnode1', 'secret', 'some.host.fsq', 7625)

        """

        self.fsq_packet.state = FsqProtocolState.FSQ_CONNECT
        self.fsq_packet.data = FsqLogin(node=node.encode('ascii'),
                                        password=password.encode('ascii'),
                                        hostname=hostname.encode('ascii'),
                                        port=port)

        fsq_packet_packed = struct.pack(PackUnpackFormat.CONNECT,
                                        self.fsq_packet.ver,
                                        self.fsq_packet.error.rc,
                                        self.fsq_packet.error.strerror,
                                        self.fsq_packet.state,
                                        self.fsq_packet.data.node,
                                        self.fsq_packet.data.password,
                                        self.fsq_packet.data.hostname,
                                        self.fsq_packet.data.port)

        try:
            hostent = socket.gethostbyname(hostname)
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((hostent, port))

            self.sock.sendall(fsq_packet_packed)
            recv_packed = self.sock.recv(FSQ_PACKET_LENGTH, socket.MSG_WAITALL)
            recv_unpacked = struct.unpack(PackUnpackFormat.CONNECT, recv_packed)
            self.__verify_fsq_packet(recv_unpacked,
                                     (FsqProtocolState.FSQ_CONNECT | FsqProtocolState.FSQ_REPLY))
            self.hostname_logging = hostname
            logging.info('connect sucessfully to FSQ server %s:%s', self.hostname_logging, port)
            logging.debug(self.fsq_packet)

        except socket.gaierror as e:
            logging.error('gethostbyname error: %s', e)
            raise

        except socket.error as e:
            logging.error('socket error: %s', e)
            raise

        except FsqProtocolError as e:
            logging.error(e)
            raise

        except FsqServerError as e:
            logging.error(e)
            raise

        except Exception as e:
            logging.error('unexpected error: %s', e)
            raise

    def open(self, fs: str, fpath: str, desc: str, dest: FsqStorageDest) -> None:
        """Open file on the FSQ server side for storing data.

        Sends FSQ_OPEN packet to FSQ server which initiates a file creation
        on the server side. Subsequently calling :func:`fsq.api.write` fills
        the file buffer on the server side.

        Parameters
        ----------
        fs : str
            Filespace name, usually the mount point (e.g. /lustre or C:).
        fpath : str
            Filepath name compound of fs + fpath (e.g /lustre/experiment/data/d1.raw).
        desc : str
            Description of the file content.
        dest : Storage destination:
            :func:`fsq.struct.FsqStorageDest.FSQ_STORAGE_NULL`
            :func:`fsq.struct.FsqStorageDest.FSQ_STORAGE_LOCAL`
            :func:`fsq.struct.FsqStorageDest.FSQ_STORAGE_LUSTRE`
            :func:`fsq.struct.FsqStorageDest.FSQ_STORAGE_TSM`
            :func:`fsq.struct.FsqStorageDest.FSQ_STORAGE_LUSTRE_TSM`

        Examples
        --------
        open('/lustre', '/lustre/experiment/data/d1.raw',
            'Some data', FSQ_STORAGE_LUSTRE_TSM)`

        """

        self.fsq_packet.state = FsqProtocolState.FSQ_OPEN
        self.fsq_packet.data = FsqInfo(fs=fs.encode('ascii'),
                                       fpath=fpath.encode('ascii'),
                                       desc=desc.encode('ascii'),
                                       fsq_storage_dest=dest)

        fsq_packet_packed = struct.pack(PackUnpackFormat.OPEN,
                                        self.fsq_packet.ver,
                                        self.fsq_packet.error.rc,
                                        self.fsq_packet.error.strerror,
                                        self.fsq_packet.state,
                                        self.fsq_packet.data.fs,
                                        self.fsq_packet.data.fpath,
                                        self.fsq_packet.data.desc,
                                        self.fsq_packet.data.fsq_storage_dest)

        try:
            self.sock.sendall(fsq_packet_packed)
            recv_packed = self.sock.recv(FSQ_PACKET_LENGTH, socket.MSG_WAITALL)
            recv_unpacked = struct.unpack(PackUnpackFormat.OPEN, recv_packed)
            self.__verify_fsq_packet(recv_unpacked,
                                     (FsqProtocolState.FSQ_OPEN | FsqProtocolState.FSQ_REPLY))
            self.fpath_logging = fpath
            logging.info('opened sucessfully on FSQ server file %s', self.fpath_logging)
            logging.debug(self.fsq_packet)

        except socket.error as e:
            logging.error('socket error: %s', e)
            raise

        except FsqProtocolError as e:
            logging.error(e)
            raise

        except FsqServerError as e:
            logging.error(e)
            raise

        except Exception as e:
            logging.error('unexpected error: %s', e)
            raise

    def write(self, buf: bytes, size: int) -> None:
        """Write buffer to TCP socket for sending it FSQ server.

        Write buffer to TCP socket. On the FSQ server side
        the buffer is written to an open file which was specified
        in prior :func:`fsq.api.open` and :func:`fsq.struct.FsqInfo`.

        Parameters
        ----------
        buf : bytes
            Buffer containing raw data.
        size : int
            Length of the buffer to write.

        """

        self.fsq_packet.state = FsqProtocolState.FSQ_DATA
        self.fsq_packet.data = FsqData(size = size)

        fsq_packet_packed = struct.pack(PackUnpackFormat.DATA,
                                        self.fsq_packet.ver,
                                        self.fsq_packet.error.rc,
                                        self.fsq_packet.error.strerror,
                                        self.fsq_packet.state,
                                        self.fsq_packet.data.size)

        try:
            self.sock.sendall(fsq_packet_packed)
            self.sock.sendall(buf)
            recv_packed = self.sock.recv(FSQ_PACKET_LENGTH, socket.MSG_WAITALL)
            recv_unpacked = struct.unpack(PackUnpackFormat.DATA, recv_packed)
            self.__verify_fsq_packet(recv_unpacked,
                                     (FsqProtocolState.FSQ_DATA | FsqProtocolState.FSQ_REPLY))
            logging.info('send sucessfully %s bytes to file %s on FSQ server',
                         self.fsq_packet.data.size, self.fpath_logging)
            logging.debug(self.fsq_packet)

        except socket.error as e:
            logging.error('socket error: %s', e)
            raise

        except FsqProtocolError as e:
            logging.error(e)
            raise

        except FsqServerError as e:
            logging.error(e)
            raise

        except Exception as e:
            logging.error('unexpected error: %s', e)
            raise

    def close(self) -> None:
        """Close file on the FSQ server side.

        Sends FSQ_CLOSE packet to FSQ server and closes the data transfer.
        The FSQ server closes the underlying file descriptor and stores the
        transfered data in a file specified by the client in
        :func:`fsq.struct.FsqInfo`.

        Raises:
            socket.error: If there is a socket-related error.
            FsqProtocolError: If there is a protocol miscommunication.
            FsqServerError: If there is a server side error.
            Exception: For any unexpected error not covered by specific handlers.
        """

        self.fsq_packet.state = FsqProtocolState.FSQ_CLOSE
        fsq_packet_packed = struct.pack(PackUnpackFormat.CLOSE,
                                        self.fsq_packet.ver,
                                        self.fsq_packet.error.rc,
                                        self.fsq_packet.error.strerror,
                                        self.fsq_packet.state)

        try:
            self.sock.sendall(fsq_packet_packed)
            recv_packed = self.sock.recv(FSQ_PACKET_LENGTH, socket.MSG_WAITALL)
            recv_unpacked = struct.unpack(PackUnpackFormat.CLOSE, recv_packed)
            self.__verify_fsq_packet(recv_unpacked,
                                     (FsqProtocolState.FSQ_CLOSE | FsqProtocolState.FSQ_REPLY))
            logging.info('closed sucessfully on FSQ server file %s', self.fpath_logging)
            logging.debug(self.fsq_packet)

        except socket.error as e:
            logging.error('socket error: %s', e)
            raise

        except FsqProtocolError as e:
            logging.error(e)
            raise

        except FsqServerError as e:
            logging.error(e)
            raise

        except Exception as e:
            logging.error('unexpected error: %s', e)
            raise

    def disconnect(self) -> None:
        """Close communication socket with FSQ server

        Sends FSQ_DISCONNECT packet to FSQ server and closes the
        communication socket with FSQ server.

        Raises:
            socket.error: If there is a socket-related error.
            FsqProtocolError: If there is a protocol miscommunication.
            FsqServerError: If there is a server side error.
            Exception: For any unexpected error not covered by specific handlers.
        """

        self.fsq_packet.state = FsqProtocolState.FSQ_DISCONNECT
        fsq_packet_packed = struct.pack(PackUnpackFormat.DISCONNECT,
                                        self.fsq_packet.ver,
                                        self.fsq_packet.error.rc,
                                        self.fsq_packet.error.strerror,
                                        self.fsq_packet.state)

        try:
            self.sock.sendall(fsq_packet_packed)
            self.sock.close()
            logging.info('disconnect sucessfully from FSQ server %s', self.hostname_logging)
            logging.debug(self.fsq_packet)

        except socket.error as e:
            logging.error('socket error: %s', e)
            raise

        except FsqProtocolError as e:
            logging.error(e)
            raise

        except FsqServerError as e:
            logging.error(e)
            raise

        except Exception as e:
            logging.error('unexpected error: %s', e)
            raise
