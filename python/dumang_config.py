"""Dumang DK6 Configuration Tool.

Usage:
  dumang_config.py dump
  dumang_config.py config <file>
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

from dumang_common import *
from dumang_gui import *

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def init_send_threads(kbd1, kbd2):
    s1 = Job(target=kbd1.send_thread, daemon=True)
    s2 = Job(target=kbd2.send_thread, daemon=True)
    return [s1, s2]

def init_receive_threads(kbd1, kbd2):
    r1 = Job(target=kbd1.receive_thread, daemon=True)
    r2 = Job(target=kbd2.receive_thread, daemon=True)
    return [r1, r2]

def configure_keys(cfg, b):
    for k in cfg:
        key = int(k.split('_')[1])
        layer_keycodes = {}
        for l in cfg[k]:
            layer = int(l.split('_')[1])
            layer_keycodes[layer] = Keycode.fromstr(cfg[k][l])

        b.put(KeyConfigurePacket(key, layer_keycodes))

def configure_board(cfg, b):
    for kbd in cfg:
        if cfg[kbd]['serial'] == b.serial:
            configure_keys(cfg[kbd]['keys'], b)

if __name__ == "__main__":
    arguments = docopt(__doc__, version='Dumang DK6 Config Tool 1.0')

    threads = []
    signal.signal(signal.SIGINT, signal_handler)

    # TODO: Handle if both not connected.
    kbd1, kbd2 = initialize_devices()

    threads.extend(init_send_threads(kbd1, kbd2))
    threads.extend(init_receive_threads(kbd1, kbd2))

    for t in threads:
        t.start()

    if arguments['dump']:
        configured_keys = []
        configured_keys.extend(kbd1.configured_keys)
        configured_keys.extend(kbd2.configured_keys)
        logging.info('{} keys configured.'.format(len(configured_keys)))
        sys.exit(0)
    elif arguments['config']:
        ymlfile = open(arguments['<file>'], 'r')
        cfg = yaml.load(ymlfile)
        configure_board(cfg, kbd1)
        configure_board(cfg, kbd2)
        logging.info('Configured.')
        sys.exit(0)
    elif arguments['inspect']:
        logging.info('Launching GUI')
        inspect_gui(kbd1, kbd2)

    for t in threads:
        t.join()
