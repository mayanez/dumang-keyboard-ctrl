import logging
import pyudev
from dumang_ctrl.dumang.common import *

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
        return SyncPacket(p.ID, press, p.layer_info)

def send_response(p, q):
    response = None

    if isinstance(p, LayerPressPacket) or isinstance(p, LayerDepressPacket):
        response = layer_toggle_process(p)

    if response:
        q.put(response)

def sync_thread(kbd1, kbd2):
    p = kbd1.recv_q.get()
    if isinstance(p, JobKiller):
        print('sync kill')
        sys.exit(0)
    send_response(p, kbd2.send_q)
    kbd1.recv_q.task_done()

def init_synchronization_threads(kbd1, kbd2):
    s1 = Job(target=sync_thread, args=(kbd1, kbd2, ), daemon=True)
    s2 = Job(target=sync_thread, args=(kbd2, kbd1, ), daemon=True)
    return [s1, s2]

def init_send_threads(kbd1, kbd2):
    s1 = Job(target=kbd1.send_thread, daemon=True)
    s2 = Job(target=kbd2.send_thread, daemon=True)
    return [s1, s2]

def init_receive_threads(kbd1, kbd2):
    r1 = Job(target=kbd1.receive_thread, daemon=True)
    r2 = Job(target=kbd2.receive_thread, daemon=True)
    return [r1, r2]

def device_init_thread(monitor):
    threads = []

    while True:
        status = monitor.get_status()
        if status == 'ready':
            kbd1, kbd2 = initialize_devices()

            threads.extend(init_send_threads(kbd1, kbd2))
            threads.extend(init_receive_threads(kbd1, kbd2))
            threads.extend(init_synchronization_threads(kbd1, kbd2))

            for t in threads:
                t.start()
        elif status == 'wait':
            # NOTE: Kill threads and wait for devices to be reconnected.
            kbd1.kill_threads()
            kbd2.kill_threads()

            for t in threads:
                t.shutdown_flag.set()

            for t in threads:
                t.join()

            kbd1.close()
            kbd2.close()

def main():
    logger.info('Staring DuMang Layer Sync...')
    signal.signal(signal.SIGINT, signal_handler)

    monitor = USBConnectionMonitorRunner(VENDOR_ID, PRODUCT_ID)
    t = threading.Thread(target=device_init_thread, args=(monitor, ), daemon=True)
    
    monitor.start()
    t.start()

    t.join()
    monitor.join()

if __name__ == "__main__":
    main()
