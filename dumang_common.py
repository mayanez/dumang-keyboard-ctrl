INIT_CMD = 0x30
SYNC_CMD = 0x46
INFO_CMD = 0x18
LAYER_PRESS_CMD = 0x3E
LAYER_DEPRESS_CMD = 0x3C

VENDOR_ID = 0x0483
PRODUCT_ID = 0x5710

# TODO: Implement remaining packet types.
class DuMangPacket:
    def __init__(self, cmd, rawbytes):
        self.cmd = cmd
        self.rawbytes = rawbytes

    @classmethod
    def parse(cls, rawbytes):
        c = None
        cmd = rawbytes[0]

        if (cmd == LAYER_PRESS_CMD):
            c = LayerPressPacket.fromrawbytes(rawbytes)
        elif (cmd == LAYER_DEPRESS_CMD):
            c = LayerDepressPacket.fromrawbytes(rawbytes)
        elif (cmd == INIT_CMD):
            c = InitializationPacket()
        elif (cmd == SYNC_CMD):
            c = SyncPacket()
        else:
            c = cls(cmd, rawbytes[1:])

        return c

    def encode(self):
        pass

    def __repr__(self):
        return "{} - CMD:{:02X} raw:[{}]".format(self.__class__.__name__, self.cmd, ', '.join(hex(x) for x in self.rawbytes))

class InitializationPacket(DuMangPacket):
    def __init__(self):
        super().__init__(INIT_CMD, None)

    def encode(self):
        return [self.cmd, 0x00, 0x00, 0x00, 0x00]

class LayerPressPacket(DuMangPacket):
    def __init__(self, ID, flag, layer_info):
        super().__init__(LAYER_PRESS_CMD, None)
        self.ID = ID
        self.flag = flag
        self.layer_info = layer_info

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return cls(rawbytes[1], rawbytes[2], rawbytes[3])

    def __repr__(self):
        return "{} - CMD:{:02X} ID:{:02X} Flag:{:02X} LayerInfo:{:02X}".format(self.__class__.__name__, self.cmd, self.ID, self.flag, self.layer_info)

class LayerDepressPacket(DuMangPacket):
    def __init__(self, ID, flag, layer_info):
        super().__init__(LAYER_DEPRESS_CMD, None)
        self.ID = ID
        self.flag = flag
        self.layer_info = layer_info

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return cls(rawbytes[1], rawbytes[2], rawbytes[3])

    def __repr__(self):
        return "{} - CMD:{:02X} ID:{:02X} Flag:{:02X} LayerInfo:{:02X}".format(self.__class__.__name__, self.cmd, self.ID, self.flag, self.layer_info)


class SyncPacket(DuMangPacket):
    def __init__(self, ID, press, layer_info):
        super().__init__(SYNC_CMD, None)
        self.ID = ID
        self.press = press
        self.layer_info = layer_info

    def encode(self):
        return [self.cmd, 0x01, self.press, 0x00, self.ID, self.layer_info, self.layer_info & 0x03, 0x00]
