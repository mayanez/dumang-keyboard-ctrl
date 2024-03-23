![Logo](images/dumang-logo.png)

# BeyondQ DuMang Keyboard Programming Tools

![GitHub](https://img.shields.io/github/license/mayanez/dumang-keyboard-ctrl)
![PyPI](https://img.shields.io/pypi/v/dumang-ctrl)
![MadeWithPython](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)
![Maintained](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

## Installation

Please refer to the [README.md](https://github.com/mayanez/dumang-keyboard-ctrl/) in the repo for more details.

## Sync Tool

This tool is a daemon process that can be used to sync the two keyboard halves for layer functionality.

You may want to setup this tool to run at startup. Depending on your distribution `systemd` is a likely solution. See <https://github.com/arjun024/systemd-example-startup> for an example. If you installed via the AUR package this is setup automatically.

_NOTE:_ libusb does NOT raise a `HOTPLUG_EVENT_DEVICE_LEFT` event on suspend (at least on Linux). This means the sync script doesn't know the keyboard handles are invalid upon resuming. Two address this two `systemd` scripts can be used. See the `systemd/` directory in the repo. The AUR package takes this approach.

### Run

    $ dumang-sync

or

    $ python -m dumang_ctrl.tools.sync

## Programming Tool

This tool provides the ability to configure the keys on your keyboard.

### Run

    $ dumang-config --help

or

    $ python -m dumang_ctrl.tools.config --help

### Usage

#### dump

The first thing you'll want to do is `dump` your current configuration:

    $ dumang-config dump > config.yml

The configuration is a YAML file describing each _Board_ half, the attached _Key Modules_, and the keycodes associated with each _Layer_ or _Macro_. Each _Board_ and _Key Module_ will have an associated `serial` that is embedded in the hardware. Each _Key Module_ can be assigned up to four layers (eg. `layer_0` - `layer_3`) and one macro.

#### inspect

Because of the unique reconfigurability of this keyboard, it can be difficult to associated a given `serial` with a _Board_ or _Key Module_. To make this process convenient you can use the `inspect` command to launch a GUI to identify this information.

    $ dumang-config inspect

The GUI will allow you to inspect your current configuration, but most importantly, when your mouse hovers over a particular _Key Module_ on a given _Board_ the LED on the _Key Module_ will begin to flash. This allows you to identify which `serial` corresponds to a given _Key Module_ & _Board_.

#### load

The `load` command does the opposite of the `dump` command and allows one to program _Key Modules_.

    $ dumang-config load <file>

This will only load the configuration onto _Key Modules_ that are specified in the file, all other keys will be unaffected.
