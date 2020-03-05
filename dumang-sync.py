import hid
import sys
import signal

INITIALIZATION_PACKET = [0x30, 0x00, 0x00, 0x00, 0x00]
VENDOR_ID = 0x0483
PRODUCT_ID = 0x5710

class DuMangPacket:
    def __init__(self):
        self.CMD = None
        self.ID = None
        self.flag = None
        self.layer_info = None

    def __repr__(self):
        return "CMD:{:02X} ID:{:02X} Flag:{:02X} LayerInfo:{:02X}".format(self.CMD, self.ID, self.flag, self.layer_info)

    @classmethod
    def parse(cls, rawbytes):
        if (rawbytes):
            o = cls()
            o.CMD = rawbytes[0]
            o.ID = rawbytes[1]
            o.flag = rawbytes[2]
            o.layer_info = rawbytes[3]
            return o

# TODO: Implement synchronization logic.

# TODO: Need to open up both left & right devices.
def initialize_device():
    try:
        device_list = hid.enumerate(VENDOR_ID, PRODUCT_ID)
        h = hid.device()
        h.open_path(device_list[1]['path'])
        h.set_nonblocking(1)
        h.write(INITIALIZATION_PACKET)
    except IOError as ex:
        # TODO: Better error handling.
        print(ex)
        print("Likely permissions error.")

    return h

def read_packet(h):
    d = h.read(64)
    return DuMangPacket.parse(d)

def signal_handler(signal, frame):
    sys.exit(0)


if __name__ == "__main__":

    signal.signal(signal.SIGINT, signal_handler)

    h = initialize_device()

    try:
        while True:
            p = read_packet(h)
            if p:
                print(p)

    except:
        sys.exit(1)
