# FreeBSD SPI wrapper for Python

The ```pyfbsdspi-tspspi``` project contains a very thin wrapper
around the ```ioctl``` requests for the ```spigen``` device
on FreeBSD to test various hardware devices from Python. It allows
direct access to the SPI bus on devices like the RaspberryPi when running
under FreeBSD.

## Installation

```
pip install pyfbsdspi-tspspi
```

## Usage

The bus can be instantiated either using context management or by it's
constructor. One can select the bus via it's first constructor
argument (```spiDevname```):

```
from fbsdspi import FbsdSPI
from labdevs.spibus import SPIClockPolarity, SPIClockPhase
```

To instantiate via context management one can use:

```
with FbsdSPI() as spi:
    # Use spi. ....
```

To instantiate without context mangement:

```
spi = FbsdSPI()

# Use spi ...
```

In case one wants to open a different bus device - for example ```spigen0.1```
which would be the second SPI bus on a RaspberryPi one can simply specify the
name as first argument (```spiDevname```)

```
with FbsdSPI('/dev/spigen0.1') as spi1:
    # spi1. ...
```

Or without context management:

```
spi0 = FbsdSPI('/dev/spigen0.0')
spi1 = FbsdSPI('/dev/spigen0.1')
```

### Setting and querying bus clock speed

To query the bus speed one can use the ```getClockSpeed()``` method. This yields
the SPI clock frequency in Hz:

```
print(f"Current clock speed is {spi.getClockSpeed()} Hz")
```

To set the clock the counterpart ```setClockSpeed``` can be used. Again note that
this requires an integer argument in Hz:

```
spi.setClockSpeed(100000)
```

### Setting and getting the bus mode

As for any SPI abstraction library one can also set the four possible bus modes:

* Clock polarity can be either ```IDLE_HIGH``` or ```IDLE_LOW```
* Clock phase can be either ```TRAILING_EDGE``` or ```LEADING_EDGE```

```
spi.setMode(
    clockPolarity = SPIClockPolarity.IDLE_HIGH,
    clockPhase = SPIClockPhase.TRAILING_EDGE
)
```

To query the current mode one can use the `` getMode``  API:

```
print(f"Current mode: {spi.getMode()}")
# Return the tuple (SPIClockPhase, SPIClockPolarity)
```
