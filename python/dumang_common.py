INIT_CMD = 0x30
SYNC_CMD = 0x46
INFO_CMD = 0x18
LAYER_PRESS_CMD = 0x3E
LAYER_DEPRESS_CMD = 0x3C
LIGHT_PULSE_CMD = 0x2A
KEY_REPORT_REQUEST_CMD = 0x04
KEY_REPORT_RESPONSE_CMD = 0x05

VENDOR_ID = 0x0483
PRODUCT_ID = 0x5710

class Keycode:
    A = 0x04
    """``a`` and ``A``"""
    B = 0x05
    """``b`` and ``B``"""
    C = 0x06
    """``c`` and ``C``"""
    D = 0x07
    """``d`` and ``D``"""
    E = 0x08
    """``e`` and ``E``"""
    F = 0x09
    """``f`` and ``F``"""
    G = 0x0A
    """``g`` and ``G``"""
    H = 0x0B
    """``h`` and ``H``"""
    I = 0x0C
    """``i`` and ``I``"""
    J = 0x0D
    """``j`` and ``J``"""
    K = 0x0E
    """``k`` and ``K``"""
    L = 0x0F
    """``l`` and ``L``"""
    M = 0x10
    """``m`` and ``M``"""
    N = 0x11
    """``n`` and ``N``"""
    O = 0x12
    """``o`` and ``O``"""
    P = 0x13
    """``p`` and ``P``"""
    Q = 0x14
    """``q`` and ``Q``"""
    R = 0x15
    """``r`` and ``R``"""
    S = 0x16
    """``s`` and ``S``"""
    T = 0x17
    """``t`` and ``T``"""
    U = 0x18
    """``u`` and ``U``"""
    V = 0x19
    """``v`` and ``V``"""
    W = 0x1A
    """``w`` and ``W``"""
    X = 0x1B
    """``x`` and ``X``"""
    Y = 0x1C
    """``y`` and ``Y``"""
    Z = 0x1D
    """``z`` and ``Z``"""

    ONE = 0x1E
    """``1`` and ``!``"""
    TWO = 0x1F
    """``2`` and ``@``"""
    THREE = 0x20
    """``3`` and ``#``"""
    FOUR = 0x21
    """``4`` and ``$``"""
    FIVE = 0x22
    """``5`` and ``%``"""
    SIX = 0x23
    """``6`` and ``^``"""
    SEVEN = 0x24
    """``7`` and ``&``"""
    EIGHT = 0x25
    """``8`` and ``*``"""
    NINE = 0x26
    """``9`` and ``(``"""
    ZERO = 0x27
    """``0`` and ``)``"""
    ENTER = 0x28
    """Enter (Return)"""
    RETURN = ENTER
    """Alias for ``ENTER``"""
    ESCAPE = 0x29
    """Escape"""
    BACKSPACE = 0x2A
    """Delete backward (Backspace)"""
    TAB = 0x2B
    """Tab and Backtab"""
    SPACEBAR = 0x2C
    """Spacebar"""
    SPACE = SPACEBAR
    """Alias for SPACEBAR"""
    MINUS = 0x2D
    """``-` and ``_``"""
    EQUALS = 0x2E
    """``=` and ``+``"""
    LEFT_BRACKET = 0x2F
    """``[`` and ``{``"""
    RIGHT_BRACKET = 0x30
    """``]`` and ``}``"""
    BACKSLASH = 0x31
    r"""``\`` and ``|``"""
    POUND = 0x32
    """``#`` and ``~`` (Non-US keyboard)"""
    SEMICOLON = 0x33
    """``;`` and ``:``"""
    QUOTE = 0x34
    """``'`` and ``"``"""
    GRAVE_ACCENT = 0x35
    r""":literal:`\`` and ``~``"""
    COMMA = 0x36
    """``,`` and ``<``"""
    PERIOD = 0x37
    """``.`` and ``>``"""
    FORWARD_SLASH = 0x38
    """``/`` and ``?``"""

    CAPS_LOCK = 0x39
    """Caps Lock"""

    F1 = 0x3A
    """Function key F1"""
    F2 = 0x3B
    """Function key F2"""
    F3 = 0x3C
    """Function key F3"""
    F4 = 0x3D
    """Function key F4"""
    F5 = 0x3E
    """Function key F5"""
    F6 = 0x3F
    """Function key F6"""
    F7 = 0x40
    """Function key F7"""
    F8 = 0x41
    """Function key F8"""
    F9 = 0x42
    """Function key F9"""
    F10 = 0x43
    """Function key F10"""
    F11 = 0x44
    """Function key F11"""
    F12 = 0x45
    """Function key F12"""

    PRINT_SCREEN = 0x46
    """Print Screen (SysRq)"""
    SCROLL_LOCK = 0x47
    """Scroll Lock"""
    PAUSE = 0x48
    """Pause (Break)"""

    INSERT = 0x49
    """Insert"""
    HOME = 0x4A
    """Home (often moves to beginning of line)"""
    PAGE_UP = 0x4B
    """Go back one page"""
    DELETE = 0x4C
    """Delete forward"""
    END = 0x4D
    """End (often moves to end of line)"""
    PAGE_DOWN = 0x4E
    """Go forward one page"""

    RIGHT_ARROW = 0x4F
    """Move the cursor right"""
    LEFT_ARROW = 0x50
    """Move the cursor left"""
    DOWN_ARROW = 0x51
    """Move the cursor down"""
    UP_ARROW = 0x52
    """Move the cursor up"""

    KEYPAD_NUMLOCK = 0x53
    """Num Lock (Clear on Mac)"""
    KEYPAD_FORWARD_SLASH = 0x54
    """Keypad ``/``"""
    KEYPAD_ASTERISK = 0x55
    """Keypad ``*``"""
    KEYPAD_MINUS = 0x56
    """Keyapd ``-``"""
    KEYPAD_PLUS = 0x57
    """Keypad ``+``"""
    KEYPAD_ENTER = 0x58
    """Keypad Enter"""
    KEYPAD_ONE = 0x59
    """Keypad ``1`` and End"""
    KEYPAD_TWO = 0x5A
    """Keypad ``2`` and Down Arrow"""
    KEYPAD_THREE = 0x5B
    """Keypad ``3`` and PgDn"""
    KEYPAD_FOUR = 0x5C
    """Keypad ``4`` and Left Arrow"""
    KEYPAD_FIVE = 0x5D
    """Keypad ``5``"""
    KEYPAD_SIX = 0x5E
    """Keypad ``6`` and Right Arrow"""
    KEYPAD_SEVEN = 0x5F
    """Keypad ``7`` and Home"""
    KEYPAD_EIGHT = 0x60
    """Keypad ``8`` and Up Arrow"""
    KEYPAD_NINE = 0x61
    """Keypad ``9`` and PgUp"""
    KEYPAD_ZERO = 0x62
    """Keypad ``0`` and Ins"""
    KEYPAD_PERIOD = 0x63
    """Keypad ``.`` and Del"""
    KEYPAD_BACKSLASH = 0x64
    """Keypad ``\\`` and ``|`` (Non-US)"""

    APPLICATION = 0x65
    """Application: also known as the Menu key (Windows)"""
    POWER = 0x66
    """Power (Mac)"""
    KEYPAD_EQUALS = 0x67
    """Keypad ``=`` (Mac)"""
    F13 = 0x68
    """Function key F13 (Mac)"""
    F14 = 0x69
    """Function key F14 (Mac)"""
    F15 = 0x6A
    """Function key F15 (Mac)"""
    F16 = 0x6B
    """Function key F16 (Mac)"""
    F17 = 0x6C
    """Function key F17 (Mac)"""
    F18 = 0x6D
    """Function key F18 (Mac)"""
    F19 = 0x6E
    """Function key F19 (Mac)"""

    LEFT_CONTROL = 0xE0
    """Control modifier left of the spacebar"""
    CONTROL = LEFT_CONTROL
    """Alias for LEFT_CONTROL"""
    LEFT_SHIFT = 0xE1
    """Shift modifier left of the spacebar"""
    SHIFT = LEFT_SHIFT
    """Alias for LEFT_SHIFT"""
    LEFT_ALT = 0xE2
    """Alt modifier left of the spacebar"""
    ALT = LEFT_ALT
    """Alias for LEFT_ALT; Alt is also known as Option (Mac)"""
    OPTION = ALT
    """Labeled as Option on some Mac keyboards"""
    LEFT_GUI = 0xE3
    """GUI modifier left of the spacebar"""
    GUI = LEFT_GUI
    """Alias for LEFT_GUI; GUI is also known as the Windows key, Command (Mac), or Meta"""
    WINDOWS = GUI
    """Labeled with a Windows logo on Windows keyboards"""
    COMMAND = GUI
    """Labeled as Command on Mac keyboards, with a clover glyph"""
    RIGHT_CONTROL = 0xE4
    """Control modifier right of the spacebar"""
    RIGHT_SHIFT = 0xE5
    """Shift modifier right of the spacebar"""
    RIGHT_ALT = 0xE6
    """Alt modifier right of the spacebar"""
    RIGHT_GUI = 0xE7
    """GUI modifier right of the spacebar"""

    def __init__(self, keycode):
        self.keycode = keycode

    def __repr__(self):
        for attribute in Keycode.__dict__.keys():
            if attribute[:2] != '__':
                value = getattr(Keycode, attribute)
                if not callable(value):
                    if self.keycode == value:
                        return "{}".format(attribute)

        return "UNKNOWN"

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
        elif (cmd == LIGHT_PULSE_CMD):
            c = LightPulsePacket.fromrawbytes(rawbytes)
        elif (cmd == KEY_REPORT_RESPONSE_CMD):
            c = KeyReportResponsePacket.fromrawbytes(rawbytes)
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

class LightPulsePacket(DuMangPacket):
    def __init__(self, onoff, key):
        super().__init__(LIGHT_PULSE_CMD, None)
        self.onoff = 0x03 if onoff else 0x02
        self.key = key

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return cls(True if rawbytes[2] == 0x03 else False, rawbytes[1])

    def encode(self):
        return [self.cmd, self.key, self.onoff, 0x0F, 0x0F, 0x0F]

class KeyReportRequestPacket(DuMangPacket):
    def __init__(self, key):
        super().__init__(KEY_REPORT_REQUEST_CMD, None)
        self.key = key

    def encode(self):
        return [self.cmd, self.key, 0x00, 0x00, 0x00]

class KeyReportResponsePacket(DuMangPacket):
    def __init__(self, key, layer_keycodes):
        super().__init__(KEY_REPORT_RESPONSE_CMD, None)
        self.key = key
        self.layer_keycodes = layer_keycodes

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return cls(rawbytes[1], {0: Keycode(rawbytes[7]), 1: Keycode(rawbytes[8]), 2: Keycode(rawbytes[9]), 3: Keycode(rawbytes[10])})

    def __repr__(self):
        return "{} - CMD:{:02X} Key:{:02X} LayerKeycodes:{}".format(self.__class__.__name__, self.cmd, self.key, self.layer_keycodes)
