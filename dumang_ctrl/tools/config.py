"""Dumang DK6 Configuration Tool.

Usage:
  dumang_config.py dump
  dumang_config.py config [--use-dkm-index] <file>
  dumang_config.py gui
  dumang_config.py inspect
  dumang_config.py (-h | --help)
  dumang_config.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
"""

import threading
import logging
import yaml
from docopt import docopt
from collections import OrderedDict

import dumang_ctrl as pkginfo
from dumang_ctrl.dumang.common import *
# TODO: Import only if using gui.
from dumang_ctrl.dumang.gui import *

logger = logging.getLogger("DuMang Config")
logger.setLevel(logging.INFO)



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
        if not l.startswith("layer_"):
            continue
        layer = int(l.split('_')[1])
        layer_keycodes[layer] = Keycode.fromstr(cfg[l])

    b.put(KeyConfigurePacket(key, layer_keycodes))

    macro = cfg.get("macro")
    if macro:
        idx = 0
        for m in macro:
            b.put(
                MacroConfigurePacket(key, idx, MacroType.fromstr(m["type"]),
                                     Keycode.fromstr(m["key"]),
                                     int(m["delay_ms"])))
            idx += 1
        b.put(MacroConfigurePacket(key, idx, MacroType(0), Keycode(0), 0))


def configure_keys(kbd_serial, cfg, kbds, use_dkm_serial):
    n = 0
    if not use_dkm_serial:
        b = find_kbd_by_serial(kbds, kbd_serial)
        if b is None:
            logger.error(f'Board with serial {kbd_serial} not found')
            sys.exit(1)
    for k in cfg:
        logger.info(f'configure {k} {use_dkm_serial}')
        key_idx = int(k.split('_')[1], 16)
        key_serial = cfg[k].get('serial', None)
        if use_dkm_serial:
            if key_serial is None:
                logger.error(f'DKM config without serial {k}')
                sys.exit(1)
            b = None
            key = None
            for kbd in kbds:
                key = find_key_by_serial(kbd, key_serial)
                if key is not None:
                    b = kbd
                    break
            if key is None:
                logger.error(f'DKM with serial {key_serial} not found')
                sys.exit(1)
            if b.serial != kbd_serial:
                logger.warning(
                    f'DKM with serial {key_serial} found on a different board. Maybe moved from board {kbd_serial} to {b.serial} ?'
                )
            if isinstance(key, int):
                key_int = key
            else:
                key_int = key.key
            if key_int != key_idx:
                logger.warning(
                    f'DKM with serial {key_serial} changed its index from {key_idx} to {key_int}'
                )
        else:
            key = key_idx
            if key_serial is not None:
                # Sanity check.
                # If any inconsistency is found, bail out.
                key_by_serial = find_key_by_serial(b, key_serial)
                if isinstance(key_by_serial, int):
                    key_by_serial_int = key_by_serial
                else:
                    key_by_serial_int = key_by_serial.key
                if key_by_serial is None:
                    logger.error(f'DKM with serial {key_serial} not found')
                    sys.exit(1)
                if key_by_serial_int != key:
                    logger.error(
                        f'DKM with serial {key_serial} changed its index from {key_idx} to {key_by_serial_int}'
                    )
                    sys.exit(1)
        configure_key(b, key, cfg[k])
        n += 1
    return n


def configure_boards(cfg, kbds, use_dkm_serial):
    n = 0
    for kbd in cfg:
        n += configure_keys(cfg[kbd]['serial'], cfg[kbd]['keys'], kbds,
                            use_dkm_serial)
    return n


def main():
    arguments = docopt(__doc__, version='Dumang DK6 Config Tool 1.0')

    threads = []
    signal.signal(signal.SIGINT, signal_handler)

    # TODO: Can both config and sync tools run at the same time?
    kbds = initialize_devices()
    if not kbds:
        logger.error('Keyboard not detected')
        sys.exit(1)

    threads.extend(init_send_threads(kbds))
    threads.extend(init_receive_threads(kbds))

    for t in threads:
        t.start()

    if arguments['dump']:
        n = 0
        cfg_yml = NestedDict()
        for i, kbd in enumerate(kbds):
            cfg_yml['kbd_{}'.format(i)]['serial'] = kbd.serial
            for _, dkm in kbd.configured_keys.items():
                n += 1
                cfg_key = cfg_yml['kbd_{}'.format(i)]['keys']['key_{}'.format(
                    dkm.key)]
                if dkm.serial is not None:
                    cfg_key['serial'] = dkm.serial
                for l, kc in dkm.layer_keycodes.items():
                    cfg_key['layer_{}'.format(l)] = str(kc)
                if dkm.macro:
                    cfg_key['macro'] = [{
                        "type": str(m.type),
                        "key": str(m.keycode),
                        "delay_ms": m.delay,
                    } for m in dkm.macro]
            kbd.kill_threads()
        yaml.dump(cfg_yml,
                  sys.stdout,
                  allow_unicode=True,
                  default_flow_style=False,
                  sort_keys=False)
        logger.info(f'Dumped {n} keys.')
    elif arguments['config']:
        use_dkm_serial = not arguments['--use-dkm-index']
        ymlfile = open(arguments['<file>'], 'r')
        cfg = yaml.safe_load(ymlfile)
        n = configure_boards(cfg, kbds, use_dkm_serial)
        for kbd in kbds:
            kbd.kill_threads()
        logger.info(f'Configured {n} keys.')
    elif arguments['gui']:
        logger.info('Launching GUI')
        inspect_gui(*kbds)
    elif arguments['inspect']:
        # TODO: Implement
        # TODO: How to match pressed key with config...might need to track layer state to match against configured keycode:/
        configured_keys = []
        for kbd in kbds:
            configured_keys.extend(kbd.configured_keys)
        print('print pressed key config to console')

    for t in threads:
        t.join()


if __name__ == "__main__":
    main()
