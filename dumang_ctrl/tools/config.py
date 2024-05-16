import click
import logging
import signal
import sys
import json
import yaml
from collections import OrderedDict

import dumang_ctrl as pkginfo
from dumang_ctrl.dumang.common import *

logger = logging.getLogger("DuMang Config")
logger.setLevel(logging.INFO)

LABEL_LAYER_PREFIX = "layer_"
LABEL_SERIAL = "serial"
LABEL_KEY = "key"
LABEL_KEYS = "keys"
LABEL_BOARD = "board"
LABEL_MACRO = "macro"
LABEL_COLOR = "color"
LABEL_TYPE = "type"
LABEL_DELAY_MS = "delay_ms"
LABEL_NKRO = "nkro"
LABEL_REPORT_RATE = "report_rate"

CFG_YAML_FORMAT = "yaml"
CFG_JSON_FORMAT = "json"
CFG_FORMATS = [CFG_YAML_FORMAT, CFG_JSON_FORMAT]
DEFAULT_CFG_FORMAT = CFG_YAML_FORMAT

CTX_KEYBOARDS_KEY = "KEYBOARDS"
CTX_THREADS_KEY = "THREADS"


class NestedDict(OrderedDict):

    def __missing__(self, key):
        self[key] = NestedDict()
        return self[key]


# NOTE: The following is required due to a bug in PyYAML when
# it comes to outputting ints with leading zeros. This is problematic
# when outputting DKM serials since they are written as hex strings.
# REF: https://github.com/yaml/pyyaml/issues/98#issuecomment-436814271
def string_representer(dumper, value):
    TAG_STR = "tag:yaml.org,2002:str"
    if value.startswith("0"):
        return dumper.represent_scalar(TAG_STR, value, style="'")
    return dumper.represent_scalar(TAG_STR, value)


yaml.add_representer(str, string_representer)
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
    return kbd.configured_keys.get(serial, None)


def configure_layers(board, key, cfg_key):
    layer_keycodes = {}
    for layer in cfg_key:
        if not layer.startswith(LABEL_LAYER_PREFIX):
            continue
        layer_int = int(layer.split(LABEL_LAYER_PREFIX[-1])[1])
        layer_keycodes[layer_int] = Keycode.fromstr(cfg_key[layer])

    if (key.layer_keycodes != layer_keycodes):
        logger.debug(
            f"Configuring DKM serial {cfg_key[LABEL_SERIAL]} to {layer_keycodes}"
        )
        board.put(DKMConfigurePacket(key, layer_keycodes))
        return True

    return False


def configure_macro(board, key, cfg_key):
    cfg_macro = cfg_key.get(LABEL_MACRO)
    if cfg_macro:
        cfg_macro_obj_list = [
            Macro(m[LABEL_KEY], idx, m[LABEL_TYPE], int(m[LABEL_DELAY_MS]))
            for idx, m in enumerate(cfg_macro)
        ]

        if key.macro != cfg_macro_obj_list:
            logger.debug(
                f"Configuring DKM serial {cfg_key[LABEL_SERIAL]} macro")

            for m in cfg_macro_obj_list:
                board.put(m.topacket(key.key))
            board.put(
                MacroConfigurePacket(key.key,
                                     len(cfg_macro_obj_list) + 1, MacroType(0),
                                     Keycode(0), 0))
            return True

    return False


def configure_color(board, key, cfg_key):
    cfg_color = cfg_key.get(LABEL_COLOR, None)
    if cfg_color and isinstance(cfg_color, str):
        red, green, blue = tuple(int(cfg_color[i:i + 2], 16) for i in (0, 2, 4))
        if key.color != (red, green, blue):
            board.put(DKMColorConfigurePacket(key.key, red, green, blue))
            logger.debug(
                f"Configuring DKM serial {cfg_key[LABEL_SERIAL]} color to #{cfg_color}"
            )
            return True

    return False


def configure_key(board, key, cfg_key):
    did_configure = configure_layers(board, key, cfg_key)
    did_configure |= configure_macro(board, key, cfg_key)
    did_configure |= configure_color(board, key, cfg_key)

    if not did_configure:
        logger.debug(
            f"DKM serial {cfg_key[LABEL_SERIAL]} already properly configured")

    return did_configure


def configure_keys(cfg_kbd, kbds):
    n = 0
    for k in cfg_kbd[LABEL_KEYS]:
        cfg_key = k[LABEL_KEY]

        key_serial = cfg_key.get(LABEL_SERIAL, None)
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

        cfg_kbd_serial = cfg_kbd[LABEL_SERIAL]
        if board.serial != cfg_kbd_serial:
            logger.warning(
                f"DKM with serial {key_serial} found on a different board. Maybe moved from board {cfg_kbd_serial} to {board.serial} ?"
            )

        if configure_key(board, key, cfg_key):
            n += 1

    return n


def configure_boards(cfg, kbds):
    n = 0
    for cfg_kbd in cfg:
        cfg_board = cfg_kbd[LABEL_BOARD]
        n += configure_keys(cfg_board, kbds)
        board = find_kbd_by_serial(kbds, cfg_board[LABEL_SERIAL])
        if board:
            cfg_nkro = cfg_board.get(LABEL_NKRO, None)
            if cfg_nkro:
                if board.nkro != cfg_nkro:
                    logger.info(f"Configuring NKRO to: {cfg_nkro}")
                    board.put(NKROConfigurePacket(cfg_nkro))

            cfg_report_rate = cfg_board.get(LABEL_REPORT_RATE, None)
            if cfg_report_rate:
                if board.report_rate != cfg_report_rate:
                    logger.info(
                        f"Configuring Report Rate to: {cfg_report_rate}")
                    board.put(ReportRateConfigurePacket(cfg_report_rate))

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
@click.option(
    "--format", type=click.Choice(CFG_FORMATS), default=DEFAULT_CFG_FORMAT)
@click.pass_context
def dump(ctx, format):
    n = 0
    cfg_dict = []
    for _, kbd in enumerate(ctx.obj[CTX_KEYBOARDS_KEY]):
        cfg_board = {
            LABEL_BOARD: {
                LABEL_SERIAL: kbd.serial,
                LABEL_NKRO: kbd.nkro,
                LABEL_REPORT_RATE: kbd.report_rate,
                LABEL_KEYS: []
            }
        }

        cfg_keys = cfg_board[LABEL_BOARD][LABEL_KEYS]
        for _, dkm in kbd.configured_keys.items():
            cfg_key = {LABEL_KEY: NestedDict()}
            if dkm.serial is not None:
                cfg_key[LABEL_KEY][LABEL_SERIAL] = dkm.serial
            for l, kc in dkm.layer_keycodes.items():
                # NOTE: Use str() here to get ANY of the valid
                # aliases should a keycode have them.
                cfg_key[LABEL_KEY][f"{LABEL_LAYER_PREFIX}{l}"] = str(kc)
            if dkm.macro:
                cfg_key[LABEL_KEY][LABEL_MACRO] = [{
                    LABEL_TYPE: str(m.type),
                    LABEL_KEY: str(m.keycode),
                    LABEL_DELAY_MS: m.delay,
                } for m in dkm.macro]
            if dkm.color:
                cfg_key[LABEL_KEY][
                    LABEL_COLOR] = "{0:02x}{1:02x}{2:02x}".format(*dkm.color)
            cfg_keys.append(cfg_key)
            n += 1

        cfg_dict.append(cfg_board)
        kbd.kill_threads()

    if format == CFG_YAML_FORMAT:
        yaml.dump(
            cfg_dict,
            sys.stdout,
            allow_unicode=True,
            default_flow_style=False,
            sort_keys=False)
        logger.info(f"Dumped {n} keys.")
    elif format == CFG_JSON_FORMAT:
        json.dump(cfg_dict, sys.stdout, indent=2)

    for t in ctx.obj[CTX_THREADS_KEY]:
        t.join()


@cli.command(help="Load the current configuration")
@click.option(
    "--format", type=click.Choice(CFG_FORMATS), default=DEFAULT_CFG_FORMAT)
@click.argument("filename")
@click.pass_context
def load(ctx, format, filename):
    cfgfile = open(filename)
    if format == CFG_YAML_FORMAT:
        cfg = yaml.safe_load(cfgfile)
    elif format == CFG_JSON_FORMAT:
        cfg = json.load(cfgfile)

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
    kbds = ctx.obj[CTX_KEYBOARDS_KEY]
    threads = ctx.obj[CTX_THREADS_KEY]

    gui = inspect_gui(*kbds)

    for kbd in kbds:
        kbd.kill_threads()

    for t in threads:
        t.join()

    for kbd in kbds:
        kbd.close()

    sys.exit(gui)


if __name__ == "__main__":
    cli(obj={})
