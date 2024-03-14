# dumang-keyboard-ctrl

[![Release](https://img.shields.io/github/v/release/mayanez/dumang-keyboard-ctrl)](https://img.shields.io/github/v/release/mayanez/dumang-keyboard-ctrl)
[![Build status](https://img.shields.io/github/actions/workflow/status/mayanez/dumang-keyboard-ctrl/main.yml?branch=main)](https://github.com/mayanez/dumang-keyboard-ctrl/actions/workflows/main.yml?query=branch%3Amain)
[![Commit activity](https://img.shields.io/github/commit-activity/m/mayanez/dumang-keyboard-ctrl)](https://img.shields.io/github/commit-activity/m/mayanez/dumang-keyboard-ctrl)
[![License](https://img.shields.io/github/license/mayanez/dumang-keyboard-ctrl)](https://img.shields.io/github/license/mayanez/dumang-keyboard-ctrl)

Dumang DK6 Tools

## Sync Tool

This tool is a daemon process that can be used to sync the two keyboard halves for layer functionality.

You may want to setup this tool to run at startup. Depending on your distribution `systemd` is a likely solution. See https://github.com/arjun024/systemd-example-startup for an example. An Arch Linux AUR and Debian package are soon to follow which will make this seamless.

### Run

    $ dumang-sync

or

    $ python -m dumang_ctrl.tools.sync

## Programming Tool

This tool provides a very rough implementation for programming keys. Please refer to the help message for options on how to run. Essentially it uses a `config.yml` that configures each key for a given layer.
The `inspect` command launches a GUI that you can use to toggle the LED for a particular key in order to get its keycode. I'm new to GUI programming so don't expect anything fancy yet. This tool in general will require a bit more reverse engineering so stay tuned.

### Run

    $ dumang-config --help

or

    $ python -m dumang_ctrl.tools.config

### Usage

A minimal example `config.yml` file is included at the top of the repo.

It works as follows:

- The `serial` corresponds to the unique identifier for each keyboard half.
- Under `keys` you can list out the configuration you want to override for each key according to it's unique key module ID (eg. `key_00` in the example).
- Each key can be assigned up to 4 layers (eg. `layer_0` - `layer_3`).

To identify both the `serial` and key module ID you'll want to use the GUI. Once you've figured out your `config.yml` you can use `dumang-config config config.yml` to flash the keyboard halves. It will only write the keys that are specified in the file, all other keys will be unaffected.

You can generate a dump of your current config with `dumang-config dump > myconfig.yml`.
