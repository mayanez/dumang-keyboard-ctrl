![Logo](docs/images/dumang-logo.png)

# BeyondQ DuMang Keyboard Programming Tools

![GitHub](https://img.shields.io/github/license/mayanez/dumang-keyboard-ctrl)
![PyPI](https://img.shields.io/pypi/v/dumang-ctrl)
![MadeWithPython](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)
![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

This is an open-source toolset for use with the DuMang line of keyboards from [Beyond Q](www.beyondq.com/).

These keyboards are fully programmable and support multiple layers.

Supported OSes:

![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black)

![Mac OS X](https://img.shields.io/badge/mac%20os-000000?style=for-the-badge&logo=apple&logoColor=white)

_NOTE:_ For correct functionality under Linux, you need to copy the udev file provided in this repo into the appropriate directory for you distro. You might then need to call `udevadm control --reload-rules` to reload the rules.

Should you run into any problems please open an `Issue`. Hopefully I can help 😸

## Install

### Using PyPI

    $ pip install dumang-ctrl

The PyPI package can be found at https://pypi.org/project/dumang-ctrl/

### Using Arch Linux

![ArchLinux](https://img.shields.io/badge/Arch_Linux-1793D1?style=for-the-badge&logo=arch-linux&logoColor=white)

Using your AUR helper of choice install the `dumang-ctrl` [package](https://aur.archlinux.org/packages/dumang-ctrl).

## Usage

Please refer to the [Github Pages](https://mayanez.github.io/dumang-keyboard-ctrl/) or `docs/`.

## Build (for Development)

    $ make setup
    $ make build

You may activate the virtualenv by running `make shell`.
