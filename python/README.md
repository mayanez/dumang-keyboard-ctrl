# DuMang DK6 Keyboard Programming Tools

This is an open-source toolset for use with the DuMang DK6 line of keyboards from Beyong Q (www.beyondq.com/).

These keyboards are fully programmable and support multiple layers.

It is currently only support for Linux, but will eventually support other
platforms.

## Install

### Dependencies

#### Debian/Ubuntu

    $ apt-get install libusb-1.0.0-dev libudev qtbase5-dev

#### Arch Linux

    $ pacman -S libusb qt5-base

#### Python

    $ pip install hidapi pyudev docopt PyQt5

For correct functionality under Linux, you need to copy the udev file provided in this repo into the appropriate directory for you distro. You might then need to call `udevadm control --reload-rules` to reload the rules.

### Using PyPI

    $ pip install dumang-keyboard-ctrl
    
### Build from Source

1. Download the archive:
    
    $ git clone https://github.com/mayanez/dumang-keyboard-ctrl.git
    $ cd dumang-keyboard-ctrl/python
    
2. Install

    $ python setup.py install

## Tools

### Sync Tool

This tool is a daemon process that can be used to sync the two keyboard halves for layer functionality. 

You may want to setup this tool to run at startup. Depending on your distribution `systemd` is a likely solution. See https://github.com/arjun024/systemd-example-startup for an example. An Arch Linux AUR and Debian package are soon to follow which will make this seamless.

#### Run

    $ dumang-sync
     
or 

    $ python -m dumang_ctrl.tools.sync

### Programming Tool

This tool provides a very rough implementation for programming keys. Please refer to the help message for options on how to run. Essentially it uses a `config.yml` that configures each key for a given layer.
The `inspect` command launches a GUI that you can use to toggle the LED for a particular key in order to get its keycode. I'm new to GUI programming so don't expect anything fancy yet. This tool in general will require a bit more reverse engineering so stay tuned.

#### Run

    $ dumang-config --help

or 

    $ python -m dumang_ctrl.tools.config
