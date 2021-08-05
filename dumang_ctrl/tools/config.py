"""Dumang DK6 Configuration Tool.

Usage:
  dumang_config.py dump
  dumang_config.py config <file>
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

from dumang_ctrl.dumang.common import *
# TODO: Import only if using gui.
from dumang_ctrl.dumang.gui import *

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

class NestedDict(OrderedDict):
    def __missing__(self, key):
        self[key] = NestedDict()
        return self[key]

yaml.add_representer(NestedDict, yaml.representer.Representer.represent_dict)

def init_send_threads(kbds):
    return [Job(target=kbd.send_thread, daemon=True) for kbd in kbds]

def init_receive_threads(kbds):
    return [Job(target=kbd.receive_thread, daemon=True) for kbd in kbds]

def configure_keys(cfg, b):
    for k in cfg:
        key = int(k.split('_')[1], 16)
        layer_keycodes = {}
        for l in cfg[k]:
            layer = int(l.split('_')[1])
            layer_keycodes[layer] = Keycode.fromstr(cfg[k][l])

        b.put(KeyConfigurePacket(key, layer_keycodes))

def configure_board(cfg, b):
    for kbd in cfg:
        if cfg[kbd]['serial'] == b.serial:
            configure_keys(cfg[kbd]['keys'], b)

def main():
    arguments = docopt(__doc__, version='Dumang DK6 Config Tool 1.0')

    threads = []
    signal.signal(signal.SIGINT, signal_handler)

    # TODO: Can both config and sync tools run at the same time?
    kbds = initialize_devices()
    if not kbds:
        logging.error('Keyboard not detected')
        sys.exit(1)

    threads.extend(init_send_threads(kbds))
    threads.extend(init_receive_threads(kbds))

    for t in threads:
        t.start()

    if arguments['dump']:
        cfg_yml = NestedDict()
        for i, kbd in enumerate(kbds):
            cfg_yml['kbd_{}'.format(i)]['serial'] = kbd.serial
            for _, dkm in kbd.configured_keys.items():
                for l, kc in dkm.layer_keycodes.items():
                    cfg_yml['kbd_{}'.format(i)]['keys']['key_{}'.format(dkm.key)]['layer_{}'.format(l)] = str(kc)
        yaml.dump(cfg_yml, sys.stdout, allow_unicode=True, default_flow_style=False, sort_keys=False)
        sys.exit(0)
    elif arguments['config']:
        ymlfile = open(arguments['<file>'], 'r')
        cfg = yaml.load(ymlfile)
        for kbd in kbds:
            configure_board(cfg, kbd)
        logging.info('Configured.')
        sys.exit(0)
    elif arguments['gui']:
        logging.info('Launching GUI')
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
