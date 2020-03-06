import threading
import logging
from dumang_common import *

logger = logging.getLogger(__name__)

# NOTE: Enable for debugging
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

def layer_toggle_process(p):
    press = 0
    half = 0

    if (p.cmd == LAYER_PRESS_CMD):
        press = 0x03
    elif (p.cmd == LAYER_DEPRESS_CMD):
        press = 0x02

    # TODO: It doesn't seem like this makes a difference.
    # if (p.ID == 0x25):
    #     half = 0x01
    # elif (p.ID == 0x0D):
    #     half = 0x02

    if (press > 0):
        return SyncPacket(p.ID, press, p.layer_info).encode()

def send_response(h, p):
    response = None

    if isinstance(p, LayerPressPacket) or isinstance(p, LayerDepressPacket):
        response = layer_toggle_process(p)

    if response:
        h.write(response)

def response_thread(h, q):
    while True:
        p = q.get()
        send_response(h, p)
        q.task_done()

def init_synchronization_threads(h, h2, q, q2):
    s1 = threading.Thread(target=response_thread, args=(h, q2, ), daemon=True)
    s2 = threading.Thread(target=response_thread, args=(h2, q, ), daemon=True)
    return [s1, s2]

def init_receive_threads(h, h2, q, q2):
    r1 = threading.Thread(target=receive_thread, args=(h, q, ), daemon=True)
    r2 = threading.Thread(target=receive_thread, args=(h2, q2, ), daemon=True)
    return [r1, r2]

if __name__ == "__main__":

    threads = []
    signal.signal(signal.SIGINT, signal_handler)

    q = queue.Queue()
    q2 = queue.Queue()

    # TODO: Handle if only one half
    h, h2 = initialize_devices()

    threads.extend(init_receive_threads(h, h2, q, q2))
    threads.extend(init_synchronization_threads(h, h2, q, q2))

    for t in threads:
        t.start()

    for t in threads:
        t.join()
