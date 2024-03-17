import click
import logging
import signal
import sys
import yaml
from collections import OrderedDict

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
YAML_LABEL_NKRO = "nkro"

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
    return kbd.configured_keys[serial]


def configure_key(board, key, cfg_key):
    layer_keycodes = {}
    did_configure = False
    for layer in cfg_key:
        if not layer.startswith(YAML_LABEL_LAYER_PREFIX):
            continue
        layer_int = int(layer.split(YAML_LABEL_LAYER_PREFIX[-1])[1])
        layer_keycodes[layer_int] = Keycode.fromstr(cfg_key[layer])

    if (key.layer_keycodes != layer_keycodes):
        logger.debug(
            f"Configuring DKM serial {cfg_key[YAML_LABEL_SERIAL]} to {layer_keycodes}"
        )
        board.put(KeyConfigurePacket(key, layer_keycodes))
        did_configure = True
    else:
        logger.debug(
            f"DKM serial {cfg_key[YAML_LABEL_SERIAL]} already properly configured"
        )

    cfg_macro = cfg_key.get(YAML_LABEL_MACRO)
    if cfg_macro:
        logger.debug(
            f"Configuring DKM serial {cfg_key[YAML_LABEL_SERIAL]} macro")

        cfg_macro_obj_list = [
            Macro(m[YAML_LABEL_KEY], idx, m[YAML_LABEL_TYPE],
                  int(m[YAML_LABEL_DELAY_MS]))
            for idx, m in enumerate(cfg_macro)
        ]

        if key.macro != cfg_macro_obj_list:
            print("not equal")
            print(key.macro)
            print(cfg_macro_obj_list)

            for m in cfg_macro_obj_list:
                board.put(m.topacket(key.key))
            board.put(
                MacroConfigurePacket(key.key,
                                     len(cfg_macro_obj_list) + 1, MacroType(0),
                                     Keycode(0), 0))
            did_configure = True

    return did_configure


def configure_keys(cfg_kbd, kbds):
    n = 0
    for k in cfg_kbd[YAML_LABEL_KEYS]:
        cfg_key = k[YAML_LABEL_KEY]

        key_serial = cfg_key.get(YAML_LABEL_SERIAL, None)
        if key_serial is None:
            logger.error(f"DKM config without serial {k}")
            sys.exit(1)

        board = None
        for kbd in kbds:
            key = find_key_by_serial(kbd, key_serial)
            if key is not None:
                board = kbd
                break
        if key is None:
            logger.error(f"DKM with serial {key_serial} not found")
            sys.exit(1)

        cfg_kbd_serial = cfg_kbd[YAML_LABEL_SERIAL]
        if board.serial != cfg_kbd_serial:
            logger.warning(
                f"DKM with serial {key_serial} found on a different board. Maybe moved from board {cfg_kbd_serial} to {b.serial} ?"
            )

        if configure_key(board, key, cfg_key):
            n += 1

    return n


def configure_boards(cfg, kbds):
    n = 0
    for cfg_kbd in cfg:
        cfg_board = cfg_kbd[YAML_LABEL_BOARD]
        n += configure_keys(cfg_board, kbds)
        board = find_kbd_by_serial(kbds, cfg_board[YAML_LABEL_SERIAL])
        if board:
            nkro = cfg_board.get(YAML_LABEL_NKRO, DEFAULT_NKRO_VALUE)
            logger.info(f"Configuring NKRO to: {nkro}")
            board.put(NKROConfigurePacket(nkro))

    return n


@click.group(help="Configuration Tool", invoke_without_command=True)
@click.option("--verbose", help="Enable Verbose Logging", is_flag=True)
@click.option(
    "--very-verbose", help="Enable Very Verbose Logging", is_flag=True)
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
        cfg_board = {
            YAML_LABEL_BOARD: {
                YAML_LABEL_SERIAL: kbd.serial,
                YAML_LABEL_NKRO: kbd.nkro,
                YAML_LABEL_KEYS: []
            }
        }

        cfg_keys = cfg_board[YAML_LABEL_BOARD][YAML_LABEL_KEYS]
        for _, dkm in kbd.configured_keys.items():
            cfg_key = {YAML_LABEL_KEY: NestedDict()}
            if dkm.serial is not None:
                cfg_key[YAML_LABEL_KEY][YAML_LABEL_SERIAL] = dkm.serial
            for l, kc in dkm.layer_keycodes.items():
                # NOTE: Use str() here to get ANY of the valid
                # aliases should a keycode have them.
                cfg_key[YAML_LABEL_KEY][f"{YAML_LABEL_LAYER_PREFIX}{l}"] = str(
                    kc)
            if dkm.macro:
                cfg_key[YAML_LABEL_KEY][YAML_LABEL_MACRO] = [{
                    YAML_LABEL_TYPE: str(m.type),
                    YAML_LABEL_KEY: str(m.keycode),
                    YAML_LABEL_DELAY_MS: m.delay,
                } for m in dkm.macro]
            cfg_keys.append(cfg_key)
            n += 1

        cfg_yml.append(cfg_board)
        kbd.kill_threads()

    yaml.dump(
        cfg_yml,
        sys.stdout,
        allow_unicode=True,
        default_flow_style=False,
        sort_keys=False)
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
