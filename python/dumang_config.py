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

def init_send_threads(h, h2, q, q2):
    s1 = threading.Thread(target=send_thread, args=(h, q, ), daemon=True)
    s2 = threading.Thread(target=send_thread, args=(h2, q2, ), daemon=True)
    return [s1, s2]

def init_receive_threads(h, h2):
    r1 = threading.Thread(target=receive_thread, args=(h, None, ), daemon=True)
    r2 = threading.Thread(target=receive_thread, args=(h2, None, ), daemon=True)
    return [r1, r2]

def configure_keys(cfg, q):
    for k in cfg:
        key = int(k.split('_')[1])
        layer_keycodes = {}
        for l in cfg[k]:
            layer = int(l.split('_')[1])
            layer_keycodes[layer] = Keycode.fromstr(cfg[k][l])

        q.put(KeyConfigurePacket(key, layer_keycodes))

def dump_current_configuration(q):
    # TODO: Populate according to actually connected keys.
    for k in range(MAX_KEYS):
        q.put(KeyReportRequestPacket(k))
    while True:
        if q.empty():
            sys.exit(0)

if __name__ == "__main__":
    arguments = docopt(__doc__, version='Dumang DK6 Config Tool 1.0')

    threads = []
    signal.signal(signal.SIGINT, signal_handler)

    q = queue.Queue()
    q2 = queue.Queue()

    h, h2 = initialize_devices()

    threads.extend(init_send_threads(h, h2, q, q2))
    threads.extend(init_receive_threads(h, h2))

    for t in threads:
        t.start()

    if arguments['dump']:
        dump_current_configuration(q, q2)
    elif arguments['config']:
        ymlfile = open(arguments['<file>'], 'r')
        cfg = yaml.load(ymlfile)
        configure_keys(cfg, q, q2)
    elif arguments['inspect']:
        inspect_gui(q, q2)

    for t in threads:
        t.join()
