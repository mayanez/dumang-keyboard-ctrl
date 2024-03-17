import click
import logging
import threading
import signal

import dumang_ctrl as pkginfo
from dumang_ctrl.dumang.common import *

logger = logging.getLogger("DuMang Sync")
logger.setLevel(logging.INFO)


def layer_toggle_process(p):
    press = 0

    if p.cmd == LAYER_PRESS_CMD:
        press = 0x03
    elif p.cmd == LAYER_DEPRESS_CMD:
        press = 0x02

    if press > 0:
        return SyncPacket(p.ID, press, p.layer_info)


def send_response(p, q):
    response = None

    if isinstance(p, (LayerPressPacket, LayerDepressPacket)):
        response = layer_toggle_process(p)

    if response:
        q.put(response)


def sync_thread(kbd1, kbd2):
    p = kbd1.recv_q.get()
    if isinstance(p, JobKiller):
        logger.debug("Kill Sync Thread")
        return
    send_response(p, kbd2.send_q)
    kbd1.recv_q.task_done()


def init_synchronization_threads(kbd1, kbd2):
    s1 = Job(
        target=sync_thread,
        args=(
            kbd1,
            kbd2,
        ),
        daemon=True,
    )
    s2 = Job(
        target=sync_thread,
        args=(
            kbd2,
            kbd1,
        ),
        daemon=True,
    )
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
    kbd1 = None
    kbd2 = None

    while True:
        status = monitor.get_status()
        if status == NOTIFY_STATUS_READY:
            logger.debug("Keyboards Detected!")
            logger.debug("Initializing...")
            kbd1, kbd2 = initialize_devices()

            logger.debug("Starting sync threads...")
            threads.extend(init_send_threads(kbd1, kbd2))
            threads.extend(init_receive_threads(kbd1, kbd2))
            threads.extend(init_synchronization_threads(kbd1, kbd2))

            for t in threads:
                t.start()
        elif status == NOTIFY_STATUS_WAIT:
            logger.debug("Keyboard Disconnected!")
            logger.debug("Stopping sync threads...")
            # NOTE: Kill threads and wait for devices to be reconnected.
            kbd1.kill_threads()
            kbd2.kill_threads()

            for t in threads:
                t.stop()

            for t in threads:
                t.join()

            kbd1.close()
            kbd2.close()
        elif status == NOTIFY_STATUS_STOP:
            logger.debug("Stopping sync threads...")

            if not kbd1 or not kbd2:
                logger.info(
                    "Could not find devices. Make sure you've setup udev rules!"
                )
                return

            kbd1.kill_threads()
            kbd2.kill_threads()

            for t in threads:
                t.stop()

            for t in threads:
                t.join()

            kbd1.close()
            kbd2.close()
            return


monitor = USBConnectionMonitorRunner(VENDOR_ID, PRODUCT_ID)
device_thread = threading.Thread(
    target=device_init_thread, args=(monitor,), daemon=True)


def sync_terminate_handler(signal, frame):
    monitor.stop()
    device_thread.join()
    monitor.join()


def sync():
    logger.info("Staring DuMang Layer Sync...")
    signal.signal(signal.SIGINT, sync_terminate_handler)

    monitor.start()
    device_thread.start()

    device_thread.join()
    monitor.join()


@click.command(help="Enable Layer Sync between two keyboard halves")
@click.option("--verbose", help="Enable Verbose Logging", is_flag=True)
@click.option(
    "--very-verbose", help="Enable Very Verbose Logging", is_flag=True)
@click.option("--version", help="Print Version", is_flag=True)
def cli(verbose, very_verbose, version):
    if very_verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    elif verbose:
        logger.setLevel(logging.DEBUG)

    if version:
        click.echo(f"{pkginfo.description}")
        click.echo(f"Version: {pkginfo.version}")
        click.echo(f"Report issues to: {pkginfo.url}")
        return

    sync()


if __name__ == "__main__":
    cli()
