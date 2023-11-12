# SPI wrapper for FreeBSD

This is a simple collection of wrappers for the ```spigen``` device
on FreeBSD that allow access to the device from various languages.
Currently this repository contains:

* A Python wrapper based on the ```ioctl``` interface of the ```fcntl```
  module. This is an implementation of the ```SPIBus``` class of the
  [labdevices SPIBus base class](https://github.com/tspspi/pylabdevs)
