# DuMang DK6 Keyboard Programming Tools
![GitHub](https://img.shields.io/github/license/mayanez/dumang-keyboard-ctrl)
![PyPI](https://img.shields.io/pypi/v/dumang-ctrl)

This is an open-source toolset for use with the DuMang DK6 line of keyboards from Beyong Q (www.beyondq.com/).

These keyboards are fully programmable and support multiple layers.

It currently supports:

* Linux
* Mac OS X

*NOTE:* For correct functionality under Linux, you need to copy the udev file provided in this repo into the appropriate directory for you distro. You might then need to call `udevadm control --reload-rules` to reload the rules.

## Install

### Using PyPI

    $ pip install dumang-ctrl
    
### Build from Source

    $ git clone https://github.com/mayanez/dumang-keyboard-ctrl.git
    $ cd dumang-keyboard-ctrl
    $ python setup.py install

### Dependencies

Please see the corresponding files in the `install` directory.

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
