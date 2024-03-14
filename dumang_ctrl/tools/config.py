import logging
import sys
from collections import OrderedDict

import click
import yaml

import dumang_ctrl as pkginfo
from dumang_ctrl.dumang.common import *

logger = logging.getLogger("DuMang Config")
logger.setLevel(logging.INFO)

YAML_LABEL_LAYER_PREFIX = "layer_"
YAML_LABEL_SERIAL = "serial"
YAML_LABEL_KEY = "key"
YAML_LABEL_KEYS = "keys"
YAML_LABEL_BOARD = "board"
YAML_LABEL_MACRO = "macro"
YAML_LABEL_TYPE = "type"
YAML_LABEL_DELAY_MS = "delay_ms"

CTX_KEYBOARDS_KEY = "KEYBOARDS"
CTX_THREADS_KEY = "THREADS"


class NestedDict(OrderedDict):
    def __missing__(self, key):
        self[key] = NestedDict()
        return self[key]


yaml.add_representer(NestedDict, yaml.representer.Representer.represent_dict)


def init_send_threads(kbds):
    return [Job(target=kbd.send_thread, daemon=True) for kbd in kbds]


def init_receive_threads(kbds):
    return [Job(target=kbd.receive_thread, daemon=True) for kbd in kbds]


def find_kbd_by_serial(kbds, serial):
    for kbd in kbds:
        if kbd.serial == serial:
            return kbd
    return None


def find_key_by_serial(kbd, serial):
    for _, dkm in kbd.configured_keys.items():
        if dkm.serial == serial:
            return dkm.key
    return None


def configure_key(b, key, cfg):
    layer_keycodes = {}
    for l in cfg:
        if not l.startswith(YAML_LABEL_LAYER_PREFIX):
            continue
        layer = int(l.split(YAML_LABEL_LAYER_PREFIX[-1])[1])
        layer_keycodes[layer] = Keycode.fromstr(cfg[l])

    b.put(KeyConfigurePacket(key, layer_keycodes))

    macro = cfg.get(YAML_LABEL_MACRO)
    if macro:
        idx = 0
        for m in macro:
            b.put(
                MacroConfigurePacket(
                    key, idx, MacroType.fromstr(m["type"]), Keycode.fromstr(m["key"]), int(m["delay_ms"])
                )
            )
            idx += 1
        b.put(MacroConfigurePacket(key, idx, MacroType(0), Keycode(0), 0))


def configure_keys(kbd_serial, cfg, kbds):
    n = 0
    for k in cfg:
        key_serial = cfg[k].get(YAML_LABEL_SERIAL, None)
        if key_serial is None:
            logger.error(f"DKM config without serial {k}")
            sys.exit(1)
        b = None
        key = None
        for kbd in kbds:
            key = find_key_by_serial(kbd, key_serial)
            if key is not None:
                b = kbd
                break
        if key is None:
            logger.error(f"DKM with serial {key_serial} not found")
            sys.exit(1)
        if b.serial != kbd_serial:
            logger.warning(
                f"DKM with serial {key_serial} found on a different board. Maybe moved from board {kbd_serial} to {b.serial} ?"
            )

        configure_key(b, key, cfg[k])
        n += 1
    return n


def configure_boards(cfg, kbds):
    n = 0
    for kbd in cfg:
        n += configure_keys(cfg[kbd][YAML_LABEL_SERIAL], cfg[kbd][YAML_LABEL_KEYS], kbds)
    return n


@click.group(help="Configuration Tool", invoke_without_command=True)
@click.option("--verbose", help="Enable Verbose Logging", is_flag=True)
@click.option("--very-verbose", help="Enable Very Verbose Logging", is_flag=True)
@click.option("--version", help="Print Version", is_flag=True)
@click.pass_context
def cli(ctx, verbose, very_verbose, version):
    signal.signal(signal.SIGINT, signal_handler)

    if very_verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif verbose:
        logger.setLevel(logging.DEBUG)

    if version:
        click.echo(f"{pkginfo.description}")
        click.echo(f"Version: {pkginfo.version}")
        click.echo(f"Report issues to: {pkginfo.url}")
        return

    # TODO: Can both config and sync tools run at the same time?
    kbds = initialize_devices()
    if not kbds:
        logger.error("Keyboard not detected")
        sys.exit(1)

    ctx.ensure_object(dict)
    ctx.obj[CTX_KEYBOARDS_KEY] = kbds
    ctx.obj[CTX_THREADS_KEY] = []

    ctx.obj[CTX_THREADS_KEY].extend(init_send_threads(kbds))
    ctx.obj[CTX_THREADS_KEY].extend(init_receive_threads(kbds))

    for t in ctx.obj[CTX_THREADS_KEY]:
        t.start()


@cli.command(help="Dump the current configuration")
@click.pass_context
def dump(ctx):
    n = 0
    cfg_yml = []
    for _i, kbd in enumerate(ctx.obj[CTX_KEYBOARDS_KEY]):
        cfg_board = {YAML_LABEL_BOARD: {YAML_LABEL_SERIAL: kbd.serial, YAML_LABEL_KEYS: []}}

        cfg_keys = cfg_board[YAML_LABEL_BOARD][YAML_LABEL_KEYS]
        for _, dkm in kbd.configured_keys.items():
            cfg_key = {YAML_LABEL_KEY: NestedDict()}
            if dkm.serial is not None:
                cfg_key[YAML_LABEL_KEY][YAML_LABEL_SERIAL] = dkm.serial
            for l, kc in dkm.layer_keycodes.items():
                # NOTE: Use str() here to get ANY of the valid
                # aliases should a keycode have them.
                cfg_key[YAML_LABEL_KEY][f"{YAML_LABEL_LAYER_PREFIX}{l}"] = str(kc)
            if dkm.macro:
                cfg_key[YAML_LABEL_KEY][YAML_LABEL_MACRO] = [
                    {
                        YAML_LABEL_TYPE: str(m.type),
                        YAML_LABEL_KEY: str(m.keycode),
                        YAML_LABEL_DELAY_MS: m.delay,
                    }
                    for m in dkm.macro
                ]
            cfg_keys.append(cfg_key)
            n += 1

        cfg_yml.append(cfg_board)
        kbd.kill_threads()

    yaml.dump(cfg_yml, sys.stdout, allow_unicode=True, default_flow_style=False, sort_keys=False)
    logger.info(f"Dumped {n} keys.")

    for t in ctx.obj[CTX_THREADS_KEY]:
        t.join()


@cli.command(help="Load the current configuration")
@click.argument("filename")
@click.pass_context
def load(ctx, filename):
    ymlfile = open(filename)
    cfg = yaml.safe_load(ymlfile)
    n = configure_boards(cfg, ctx.obj[CTX_KEYBOARDS_KEY])
    for kbd in ctx.obj[CTX_KEYBOARDS_KEY]:
        kbd.kill_threads()
    logger.info(f"Configured {n} keys.")

    for t in ctx.obj[CTX_THREADS_KEY]:
        t.join()


@cli.command(help="Inspect the current configuration via a GUI")
@click.pass_context
def inspect(ctx):
    logger.info("Launching GUI")
    from dumang_ctrl.dumang.gui import inspect_gui

    inspect_gui(*ctx.obj[CTX_KEYBOARDS_KEY])

    for t in ctx.obj[CTX_THREADS_KEY]:
        t.join()


if __name__ == "__main__":
    cli(obj={})
