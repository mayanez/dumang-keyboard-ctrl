# DuMang DK6 Keyboard Programming Tools

This is an open-source toolset for use with the DuMang DK6 line of keyboards.

These keyboards are fully programmable and support multiple layers.

## Install

### Dependencies

#### Debian/Ubuntu

    $ apt-get install libusb-1.0.0-dev libudev qtbase5-dev

#### Arch Linux

    $ pacman -S libusb qt5-base

### Python

    $ pip install hidapi docopt PyQt5

For correct functionality under Linux, you need to copy the udev file provided in this repo into the appropriate directory for you distro. You might then need to call `udevadm control --reload-rules` to reload the rules.

### C

In progress.

## Tools

### Sync Tool

The `dumang_sync.py` is a daemon process that can be used to sync the two keyboard halves.

You may want to setup this tool to run at startup. Depending on your distribution `systemd` is a likely solution. See https://github.com/arjun024/systemd-example-startup for an example.

### Programming Tool

`dumang_config.py` provides a very rough version of the programming tool. Please refer to the help message for options on how to run. Essentially it uses a `config.yml` that configures each key for a given layer.
The `inspect` command launches a GUI that you can use to toggle the LED for a particular key in order to get its keycode. I'm new to GUI programming so don't expect anything fancy yet.
