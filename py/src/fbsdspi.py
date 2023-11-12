import fcntl
import struct
import os
import ctypes

from labdevices.spibus import SPIBus, SPIClockPolarity, SPIClockPhase

class SPIGENTransfer_IOVec(ctypes.Structure):
    _fields_ = [
            ( "iov_base", ctypes.c_void_p ),
            ( "iov_len", ctypes.c_ulong )
    ]

class SPIGENTransfer(ctypes.Structure):
    _fields_ = [
        ( "st_command", SPIGENTransfer_IOVec ),
        ( "st_data", SPIGENTransfer_IOVec )
    ]

class FbsdSPI(SPIBus):
    def __init__(
        self,
        spiDevname = "/dev/spigen0.0"
    ):
        self._spidevname = spiDevname
        self._SPIGENIOC_GET_CLOCK_SPEED = 1074025218
        self._SPIGENIOC_SET_CLOCK_SPEED = 2147767043
        self._SPIGENIOC_GET_SPI_MODE    = 1074025220
        self._SPIGENIOC_SET_SPI_MODE    = 2147767045
        self._SPIGENIOC_TRANSFER        = 2148553472

        self._handle = os.open(spiDevname, os.O_RDONLY)

        # Query current mode and clock speed
        self._bus_clock = struct.unpack('i', fcntl.ioctl(self._handle, self._SPIGENIOC_GET_CLOCK_SPEED, struct.pack('i', 0)))[0]
        self._bus_mode = struct.unpack('i', fcntl.ioctl(self._handle, self._SPIGENIOC_GET_SPI_MODE, struct.pack('i', 0)))[0]

    def __del__(
        self
    ):
        try:
            os.close(self._handle)
        except:
            pass

    def __enter__(self):
        return self
    def __exit__(self, type, value, tb):
        return



    def _getClockSpeed(self):
        self._bus_clock = struct.unpack('i', fcntl.ioctl(self._handle, self._SPIGENIOC_GET_CLOCK_SPEED, struct.pack('i', 0)))[0]
        return self._bus_clock
    def _setClockSpeed(self, hz):
        fcntl.ioctl(self._handle, self._SPIGENIOC_SET_CLOCK_SPEED, struct.pack('i', hz))
        self._bus_clock = hz
        return True

    def _getMode(self):
        bMode = struct.unpack('i', fcntl.ioctl(self._handle, self._SPIGENIOC_GET_SPI_MODE, struct.pack('i', 0)))[0]
        self._bus_mode = bMode

        pol = SPIClockPolarity.IDLE_LOW
        ph = SPIClockPhase.LEADING_EDGE
        if (bMode & 0x01) != 0:
            ph = SPIClockPhase.TRAILING_EDGE
        if (bMode & 0x02) != 0:
            pol = SPIClockPolarity.IDLE_HIGH
        return ph, pol

    def _setMode(self, clockPolarity = None, clockPhase = None):
        # First get current mode ...
        ph, pol = 0
        if (clockPolarity is None) or (clockPhase is None):
            ph, pol = self._getMode()

        if clockPolarity is not None:
            if not isinstance(clockPolarity, SPIClockPolarity):
                raise ValueError("Clock polarity has to be a instance of SPIClockPolarity")
            pol = clockPolarity
        if clockPhase is not None:
            if not isinstance(clockPhase, SPIClockPhase):
                raise ValueError("Clock phase has to be an instance of SPIClockPhase")
            ph = clockPhase

        mode = ph.value | pol.value
        fcntl.ioctl(self._handle, self._SPIGENIOC_SET_SPI_MODE, struct.pack("i", mode))
        self._busMode = mode
        return True

    def _transfer(self, nbytes = None, buffer = None):
        if (nbytes is None) and (buffer is None):
            raise ValueError("Either a buffer of a byte length has to be supplied")

        if (nbytes is not None) and (buffer is not None):
            if len(buffer) != nbytes:
                raise ValueError("Mismatch between passed buffer and byte length")
        elif buffer is not None:
            nbytes = len(buffer)
        else:
            if nbytes <= 0:
                raise ValueError(f"Invalid transfer buffer size {nbytes} specified")
            buffer = bytes([0] * nbytes)

        cBuf = ctypes.create_string_buffer(buffer, len(buffer))

        iov = SPIGENTransfer()
        iov.st_command.iov_base = ctypes.cast(cBuf, ctypes.c_void_p)
        iov.st_command.iov_len = nbytes
        # We don't use the data entry
        iov.st_data.iov_base = 0
        iov.st_data.iov_len = 0

        rq2 = [ cBuf[j] for j in range(nbytes) ]
        fcntl.ioctl(self._handle, self._SPIGENIOC_TRANSFER, iov)

        # Prase buffer ...
        resp = [ cBuf[j] for j in range(nbytes) ]

        return resp

