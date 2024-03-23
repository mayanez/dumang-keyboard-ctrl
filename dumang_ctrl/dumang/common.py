import logging
import queue
import sys
import threading
from collections import deque

import hid
import usb1

logger = logging.getLogger(__name__)

BOARD_INFO_REQUEST_CMD = 0x30
BOARD_INFO_RESPONSE_CMD = 0x31
DKM_INFO_REQUEST_CMD = 0x06
DKM_INFO_RESPONSE_CMD = 0x07
BOARD_SYNC_CMD = 0x46
LAYER_PRESS_CMD = 0x3E
LAYER_DEPRESS_CMD = 0x3C
LIGHT_PULSE_CMD = 0x2A
DKM_REPORT_REQUEST_CMD = 0x04
DKM_REPORT_RESPONSE_CMD = 0x05
DKM_ADDED_CMD = 0x18
DKM_REMOVED_CMD = 0x1A
DKM_CONFIGURE_CMD = 0x09
MACRO_REPORT_REQUEST_CMD = 0x42
MACRO_REPORT_RESPONSE_CMD = 0x43
MACRO_CONFIGURE_CMD = 0x40
NKRO_CONFIGURE_CMD = 0x44
DKM_COLOR_REQUEST_CMD = 0x2C
DKM_COLOR_RESPONSE_CMD = 0x2D
DKM_COLOR_CONFIGURE_CMD = 0x2E
REPORT_RATE_CONFIGURE_CMD = 0x34

MACRO_MIN_IDX = 0x05
MACRO_MAX_IDX = 0x45
MACRO_MIN_DELAY_MS = 10
MACRO_MAX_DELAY_MS = 255 * 255 + 255

DEFAULT_NKRO_VALUE = True
DEFAULT_REPORT_RATE = 1000

VENDOR_ID = 0x0483
PRODUCT_ID = 0x5710
KBD_1_ID = 0x25
KBD_2_ID = 0x0D

# NOTE: Unless configured in "overload" mode (which is considered unstable),
# according to documentation, max amount of DKM per board is 44.
MAX_KEYS = 44
MAX_LAYERS = 4
UNKNOWN_MACROTYPE_STR = "UNKNOWN"

NOTIFY_STATUS_READY = "ready"
NOTIFY_STATUS_WAIT = "wait"
NOTIFY_STATUS_STOP = "stop"


class Keycode:
    """These are HID Keycodes and can be found here: https://usb.org/sites/default/files/hut1_3_0.pdf"""

    MACRO = 0x03
    """Macro"""

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

    LAYER_0 = 0xD0
    """Change to keyboard Layer 0"""
    LAYER_1 = 0xD1
    """Change to keyboard Layer 1"""
    LAYER_2 = 0xD2
    """Change to keyboard Layer 2"""
    LAYER_3 = 0xD3
    """Change to keyboard Layer 3"""

    LAYER_TOGGLE_0 = 0xD4
    """Change while pressing to keyboard Layer 0"""
    LAYER_TOGGLE_1 = 0xD5
    """Change while pressing to keyboard Layer 1"""
    LAYER_TOGGLE_2 = 0xD6
    """Change while pressing to keyboard Layer 2"""
    LAYER_TOGGLE_3 = 0xD7
    """Change while pressing to keyboard Layer 3"""

    LAYER_KEY_0 = 0xDC
    """Change when long pressing to keyboard Layer 0"""
    LAYER_KEY_1 = 0xDD
    """Change when long pressing to keyboard Layer 1"""
    LAYER_KEY_2 = 0xDE
    """Change when long pressing to keyboard Layer 2"""
    LAYER_KEY_3 = 0xDF
    """Change when long pressing to keyboard Layer 3"""

    LEFT_MOUSE_CLICK = 0xF6
    """Left mouse click"""
    RIGHT_MOUSE_CLICK = 0xF7
    """Right mouse click"""
    MIDDLE_MOUSE_CLICK = 0xF8
    """Middle mouse click"""

    TRANSPARENT = 0xFF
    """Transparent"""

    DISABLED = 0xFE
    """Disabled"""

    def __init__(self, keycode):
        self.keycode = keycode
        self.keystr = []

        for attribute in Keycode.__dict__:
            if attribute[:2] != "__":
                value = getattr(Keycode, attribute)
                if not callable(value) and self.keycode == value:
                    self.keystr.append(attribute)
        if not self.keystr:
            self.keystr = [f"UNKNOWN_{self.keycode:02X}"]

    def __lt__(self, other):
        return self.keycode < other.keycode

    def __eq__(self, other):
        return self.keycode == other.keycode

    def __hash__(self):
        return hash(self.keycode)

    @classmethod
    def fromstr(cls, keystr):
        for attribute in Keycode.__dict__:
            if attribute[:2] != "__":
                value = getattr(Keycode, attribute)
                if not callable(value) and keystr == attribute:
                    return cls(value)

    @classmethod
    def keys(cls):
        result = []
        for attribute in Keycode.__dict__:
            if attribute[:2] != "__":
                value = getattr(Keycode, attribute)
                if not callable(value):
                    result.append(attribute)
        return result

    def encode(self):
        return self.keycode

    def __str__(self):
        # NOTE: The first item in the list
        # will be used. This is determined by the definition
        # order in this class.
        return self.keystr[0]

    def __repr__(self):
        return "/".join(self.keystr)


class MacroType:
    KEYDOWN = 0x01
    KEYUP = 0x02
    WAIT_KEYUP = 0x04
    """Used to define Split Section Macros (ie. execute part 1 on key down and part 2 on key up)"""

    def __init__(self, type_):
        self.type = type_
        self.typestr = UNKNOWN_MACROTYPE_STR
        for attribute in MacroType.__dict__:
            if attribute[:2] != "__":
                value = getattr(MacroType, attribute)
                if not callable(value) and self.type == value:
                    self.typestr = attribute
        if self.typestr is UNKNOWN_MACROTYPE_STR:
            self.typestr = f"UNKNOWN_{self.type:02X}"

    @classmethod
    def fromstr(cls, typestr):
        for attribute in MacroType.__dict__:
            if attribute[:2] != "__":
                value = getattr(MacroType, attribute)
                if not callable(value) and typestr == attribute:
                    return cls(value)

    def __eq__(self, other):
        return self.type == other.type

    def __repr__(self):
        return self.typestr


class Macro:

    def __init__(self, keycode, idx, type, delay):
        self.keycode = Keycode.fromstr(keycode) if not isinstance(
            keycode, Keycode) else keycode
        self.idx = idx
        self.type = MacroType.fromstr(type) if not isinstance(
            type, MacroType) else type
        if delay < MACRO_MIN_DELAY_MS:
            self.delay = MACRO_MIN_DELAY_MS
            logger.warning(
                f"Cannot set macro delay less than {MACRO_MIN_DELAY_MS}. Setting to {MACRO_MIN_DELAY_MS}."
            )
        if delay > MACRO_MAX_DELAY_MS:
            self.delay = MACRO_MAX_DELAY_MS
            logger.warning(
                f"Cannot set macro delay less than {MACRO_MAX_DELAY_MS}. Setting to {MACRO_MAX_DELAY_MS}."
            )
        else:
            self.delay = delay

    def topacket(self, key):
        return MacroConfigurePacket(key, self.idx, self.type, self.keycode,
                                    self.delay)

    @classmethod
    def frompacket(cls, packet):
        if not isinstance(packet, MacroReportResponsePacket):
            logger.error("Cannot create class from this packet type!")
            return None
        return cls(packet.keycode, packet.idx, packet.type, packet.delay)

    def __eq__(self, other):
        return (self.keycode, self.idx, self.type,
                self.delay) == (other.keycode, other.idx, other.type,
                                other.delay)

    def __repr__(self):
        return f"{self.keycode}/{self.idx}/{self.type}/{self.delay}"


class Job(threading.Thread):

    def __init__(self, **kwargs):
        try:
            args = kwargs["args"]
        except KeyError:
            args = []

        super().__init__(
            target=kwargs["target"], args=args, daemon=kwargs["daemon"])
        self.shutdown_flag = threading.Event()
        self.started = False

    def run(self):
        while not self.shutdown_flag.is_set():
            self._target(*self._args, **self._kwargs)
        logger.debug("Thread Killed")

    def start(self):
        if not self.started:
            self.started = True
            super().start()
        else:
            logger.debug("Thread previously started")

    def stop(self):
        self.shutdown_flag.set()


class JobKiller:

    def __init__(self):
        self.init = True


class DuMangKeyModule:

    def __init__(self,
                 key,
                 layer_keycodes=None,
                 serial=None,
                 color=None,
                 version=None):
        assert isinstance(key, int)
        self.key = key
        self.layer_keycodes = layer_keycodes
        self.serial = serial
        self.macro = []
        self.color = color
        self.version = version

    def __lt__(self, other):
        return self.key < other.key

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def encode(self):
        return self.key

    def __repr__(self):
        return f"{self.key:02X}" if isinstance(self.key, int) else f"{self.key}"


class DuMangBoard:
    READ_TIMEOUT_MS = 50

    def __init__(self, serial, handle):
        self.serial = serial
        self.handle = handle
        self._keys_initialized = False
        self._configured_keys = {}
        self.send_q = queue.Queue()
        self.recv_q = queue.Queue()
        self.should_stop = False
        self._initialize()

    def _initialize(self):
        # NOTE: Because threads aren't started yet, it is important,
        # to use write/read_packet().
        self.write_packet(BoardInfoRequestPacket())
        p = self.read_packet()

        if isinstance(p, BoardInfoResponsePacket):
            self.nkro = p.nkro
            self.report_rate = p.report_rate
            self.version = p.version
        else:
            self.nkro = DEFAULT_NKRO_VALUE
            self.report_rate = DEFAULT_REPORT_RATE

    def write(self, rawbytes):
        self.handle.write(rawbytes)

    def read(self):
        try:
            # NOTE: Needs to be non-blocking so thread can be killed atm.
            # Ideally I prefer it to be blocking.
            return self.handle.read(64, timeout_ms=DuMangBoard.READ_TIMEOUT_MS)
        except:
            return None

    def put(self, v):
        self.send_q.put(v)

    def get(self):
        return self.recv_q.get()

    def close(self):
        # NOTE: A hacky way of verifying if the handle is still valid.
        # I wonder if there is a cleaner way to do this.
        valid = True

        try:
            self.handle.read(64, timeout_ms=DuMangBoard.READ_TIMEOUT_MS)
        except OSError:
            valid = False
        except ValueError:
            valid = False

        if valid:
            self.handle.close()

    def read_packet(self):
        d = self.read()
        return DuMangPacket.parse(d)

    def write_packet(self, p):
        self.write(p.encode())

    def kill_threads(self):
        self.send_q.put(JobKiller())
        self.recv_q.put(JobKiller())
        self.should_stop = True

    def receive_thread(self):
        p = self.read_packet()

        if p:
            logger.debug(p)
            self.recv_q.put(p)

        if self.should_stop:
            sys.exit(0)

    def send_thread(self):
        p = self.send_q.get()

        # NOTE: Allows for thread to be killed with blocking queue
        if isinstance(p, JobKiller):
            sys.exit(0)

        self.write_packet(p)

    def _handle_dkm_reports(self):
        pending = 0
        for k in range(MAX_KEYS):
            self.put(DKMReportRequestPacket(k))
            pending += 1

        while pending > 0:
            p = self.get()
            if isinstance(p, DKMReportResponsePacket):
                pending -= 1
                if any([kc.keycode != 0 for kc in p.layer_keycodes.values()]):
                    # NOTE: We add the layer_keycodes to the DKM
                    p.key.layer_keycodes = p.layer_keycodes
                    self._configured_keys[p.serial] = DuMangKeyModule(
                        p.key.key, p.layer_keycodes, p.serial)

    def _handle_dkm_macros(self):
        for _, dkm in self._configured_keys.items():
            pending = 0
            if any([
                    kc.keycode == Keycode.MACRO
                    for kc in dkm.layer_keycodes.values()
            ]):
                self.put(MacroReportRequestPacket(dkm, 0))
                pending += 1

            while pending > 0:
                p = self.get()
                if isinstance(p, MacroReportResponsePacket):
                    pending -= 1
                    if p.type.type not in [0, 0xFF]:
                        dkm.macro.append(Macro.frompacket(p))
                        self.put(MacroReportRequestPacket(dkm, p.idx + 1))
                        pending += 1

    def _handle_dkm_colors(self):
        for _, dkm in self._configured_keys.items():
            self.put(DKMColorRequestPacket(dkm))

            p = self.get()
            if isinstance(p, DKMColorResponsePacket):
                dkm.color = (p.red, p.green, p.blue)

    def _handle_dkm_info(self):
        for _, dkm in self._configured_keys.items():
            self.put(DKMInfoRequestPacket(dkm))

            p = self.get()
            if isinstance(p, DKMInfoResponsePacket):
                dkm.version = p.version

    @property
    def configured_keys(self):
        if not self._keys_initialized:
            self._handle_dkm_reports()
            self._handle_dkm_macros()
            self._handle_dkm_colors()
            self._handle_dkm_info()

            self._keys_initialized = True

        return self._configured_keys


class DuMangPacket:

    def __init__(self, cmd, rawbytes):
        self.cmd = cmd
        self.rawbytes = rawbytes

    @classmethod
    def parse(cls, rawbytes):
        c = None
        if rawbytes:
            cmd = rawbytes[0]

            if cmd == LAYER_PRESS_CMD:
                c = LayerPressPacket.fromrawbytes(rawbytes)
            elif cmd == LAYER_DEPRESS_CMD:
                c = LayerDepressPacket.fromrawbytes(rawbytes)
            elif cmd == BOARD_INFO_RESPONSE_CMD:
                c = BoardInfoResponsePacket.fromrawbytes(rawbytes)
            elif cmd == DKM_INFO_RESPONSE_CMD:
                c = DKMInfoResponsePacket.fromrawbytes(rawbytes)
            elif cmd == DKM_COLOR_RESPONSE_CMD:
                c = DKMColorResponsePacket.fromrawbytes(rawbytes)
            elif cmd == LIGHT_PULSE_CMD:
                c = LightPulsePacket.fromrawbytes(rawbytes)
            elif cmd == DKM_REPORT_RESPONSE_CMD:
                c = DKMReportResponsePacket.fromrawbytes(rawbytes)
            elif cmd == DKM_ADDED_CMD:
                c = DKMAddedPacket.fromrawbytes(rawbytes)
            elif cmd == DKM_REMOVED_CMD:
                c = DKMRemovedPacket.fromrawbytes(rawbytes)
            elif cmd == MACRO_REPORT_RESPONSE_CMD:
                c = MacroReportResponsePacket.fromrawbytes(rawbytes)
            else:
                c = cls(cmd, rawbytes[1:])

        return c

    def encode(self):
        pass

    def __repr__(self):
        return "{} - CMD:{:02X} raw:[{}]".format(
            self.__class__.__name__, self.cmd,
            ", ".join(hex(x) for x in self.rawbytes))


class BoardInfoRequestPacket(DuMangPacket):

    def __init__(self):
        super().__init__(BOARD_INFO_REQUEST_CMD, None)

    def encode(self):
        return [self.cmd, 0x00, 0x00, 0x00, 0x00]


class BoardInfoResponsePacket(DuMangPacket):
    REPORT_RATES = {
        0x0A: 100,
        0x08: 125,
        0x05: 200,
        0x04: 250,
        0x03: 333,
        0x02: 500,
        0x01: 1000
    }

    def __init__(self, report_rate, nkro_enabled, version):
        super().__init__(BOARD_INFO_RESPONSE_CMD, None)
        self.report_rate = self.REPORT_RATES[report_rate]
        # NOTE: 0x13 is False
        self.nkro = True if nkro_enabled == 0x17 else False
        self.version = version

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return cls(rawbytes[5], rawbytes[7], (rawbytes[3], rawbytes[4]))

    def __repr__(self):
        return "{} - CMD:{:02X} NKRO:{} Report Rate:{}".format(
            self.__class__.__name__, self.cmd, self.nkro, self.report_rate)


class DKMInfoRequestPacket(DuMangPacket):

    def __init__(self, key):
        super().__init__(DKM_INFO_REQUEST_CMD, None)
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key

    def encode(self):
        return [self.cmd, self.key.encode(), 0x00, 0x00, 0x00]


class DKMInfoResponsePacket(DuMangPacket):

    def __init__(self, version):
        super().__init__(DKM_INFO_RESPONSE_CMD, None)
        self.version = version

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return cls((rawbytes[3], rawbytes[4]))

    def __repr__(self):
        return "{} - CMD:{:02X} Version:{}".format(self.__class__.__name__,
                                                   self.cmd, self.version)


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
        return "{} - CMD:{:02X} ID:{:02X} Flag:{:02X} LayerInfo:{:02X}".format(
            self.__class__.__name__, self.cmd, self.ID, self.flag,
            self.layer_info)


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
        return "{} - CMD:{:02X} ID:{:02X} Flag:{:02X} LayerInfo:{:02X}".format(
            self.__class__.__name__, self.cmd, self.ID, self.flag,
            self.layer_info)


class BoardSyncPacket(DuMangPacket):

    def __init__(self, ID, press, layer_info):
        super().__init__(BOARD_SYNC_CMD, None)
        self.ID = ID
        self.press = press
        self.layer_info = layer_info

    def encode(self):
        return [
            self.cmd, 0x01, self.press, 0x00, self.ID, self.layer_info,
            self.layer_info & 0x03, 0x00
        ]


class LightPulsePacket(DuMangPacket):

    def __init__(self, onoff, key):
        super().__init__(LIGHT_PULSE_CMD, None)
        self.onoff = 0x03 if onoff else 0x02
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return cls(bool(rawbytes[2] == 3), rawbytes[1])

    def encode(self):
        return [self.cmd, self.key.encode(), self.onoff, 0x0F, 0x0F, 0x0F]


class DKMReportRequestPacket(DuMangPacket):

    def __init__(self, key):
        super().__init__(DKM_REPORT_REQUEST_CMD, None)
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key

    def encode(self):
        return [self.cmd, self.key.encode(), 0x00, 0x00, 0x00]


class KeyReportBasePacket(DuMangPacket):

    def __init__(self, cmd, key, layer_keycodes, serial):
        super().__init__(cmd, None)
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key
        self.layer_keycodes = layer_keycodes
        self.serial = serial

    @classmethod
    def fromrawbytes(cls, rawbytes):
        serial = (rawbytes[2] << 24) + (rawbytes[3] << 16) + (
            rawbytes[4] << 8) + rawbytes[5]
        return cls(
            rawbytes[1],
            {
                0: Keycode(rawbytes[7]),
                1: Keycode(rawbytes[8]),
                2: Keycode(rawbytes[9]),
                3: Keycode(rawbytes[10])
            },
            f"{serial:08X}",
        )

    def __repr__(self):
        return "{} - CMD:{:02X} Key:{} Serial:{} LayerKeycodes:{}".format(
            self.__class__.__name__, self.cmd, self.key, self.serial,
            self.layer_keycodes)


class DKMReportResponsePacket(KeyReportBasePacket):

    def __init__(self, key, layer_keycodes, serial):
        super().__init__(DKM_REPORT_RESPONSE_CMD, key, layer_keycodes, serial)

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return super().fromrawbytes(rawbytes)


class DKMAddedPacket(KeyReportBasePacket):

    def __init__(self, key, layer_keycodes, serial):
        super().__init__(DKM_ADDED_CMD, key, layer_keycodes, serial)

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return super().fromrawbytes(rawbytes)


class DKMRemovedPacket(KeyReportBasePacket):

    def __init__(self, key, layer_keycodes, serial):
        super().__init__(DKM_REMOVED_CMD, key, layer_keycodes, serial)

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return super().fromrawbytes(rawbytes)


class DKMConfigurePacket(DuMangPacket):

    def __init__(self, key, layer_keycodes):
        super().__init__(DKM_CONFIGURE_CMD, None)
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key
        self.layer_keycodes = {
            k: v.encode() if isinstance(v, Keycode) else v
            for k, v in layer_keycodes.items()
        }

    def encode(self):
        return [
            self.cmd,
            self.key.encode() + 1,
            self.layer_keycodes[1],
            self.layer_keycodes[2],
            self.layer_keycodes[3],
            0xFF,
            self.layer_keycodes[0],
        ]

    def __repr__(self):
        return f"{self.__class__.__name__} - CMD:{self.cmd:02X} Key:{self.key} LayerKeycodes:{self.layer_keycodes}"


class MacroReportRequestPacket(DuMangPacket):

    def __init__(self, key, idx):
        super().__init__(MACRO_REPORT_REQUEST_CMD, None)
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key
        self.idx = idx

    def encode(self):
        return [
            self.cmd,
            self.key.encode(), self.idx + MACRO_MIN_IDX, 0x00, 0x00
        ]


class MacroReportResponsePacket(DuMangPacket):

    def __init__(self, key, idx, type_, keycode, delay):
        super().__init__(MACRO_REPORT_RESPONSE_CMD, None)
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key
        self.idx = idx
        self.type = type_
        self.keycode = keycode
        self.delay = delay

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return cls(
            rawbytes[1],
            rawbytes[2] - MACRO_MIN_IDX,
            MacroType(rawbytes[3]),
            Keycode(rawbytes[4]),
            rawbytes[5] * 256 + rawbytes[6],
        )

    def __repr__(self):
        return "{} - CMD:{:02X} Key:{} Idx:{} Type:{} Keycode:{} Delay:{}".format(
            self.__class__.__name__, self.cmd, self.key, self.idx, self.type,
            self.keycode, self.delay)


class MacroConfigurePacket(DuMangPacket):

    def __init__(self, key, idx, type_, keycode, delay):
        super().__init__(MACRO_CONFIGURE_CMD, None)
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key
        self.idx = idx
        self.type = type_
        self.keycode = keycode
        self.delay = delay

    def encode(self):
        return [
            self.cmd,
            self.key.encode(),
            self.idx + MACRO_MIN_IDX,
            self.type.type,
            self.keycode.keycode,
            self.delay // 256,  # MAX: 255*255 + 255
            self.delay % 256,
        ]

    def __repr__(self):
        return "{} - CMD:{:02X} Key:{} Idx:{} Type:{} Keycode:{} Delay:{}".format(
            self.__class__.__name__, self.cmd, self.key, self.idx, self.type,
            self.keycode, self.delay)


class NKROConfigurePacket(DuMangPacket):

    def __init__(self, onoff):
        super().__init__(NKRO_CONFIGURE_CMD, None)
        self.onoff = 0x01 if onoff else 0x00

    def encode(self):
        return [self.cmd, 0x01, 0x04, self.onoff, 0x17, 0x20, 0x00]


class ReportRateConfigurePacket(DuMangPacket):

    REPORT_RATES = {
        100: 0x0A,
        125: 0x08,
        200: 0x05,
        250: 0x04,
        333: 0x03,
        500: 0x02,
        1000: 0x01
    }

    def __init__(self, report_rate):
        super().__init__(REPORT_RATE_CONFIGURE_CMD, None)
        if not report_rate in self.REPORT_RATES:
            logger.warning(
                f"Invalid report rate. Supported values: {self.REPORT_RATES}.")
            logger.info(f"Enabling default rate: {DEFAULT_REPORT_RATE}")
            self.report_rate = DEFAULT_REPORT_RATE
        else:
            self.report_rate = report_rate

    def encode(self):
        return [
            self.cmd, 0x00, self.REPORT_RATES[self.report_rate], 0x00, 0x00,
            0x00
        ]


class DKMColorRequestPacket(DuMangPacket):

    def __init__(self, key):
        super().__init__(DKM_COLOR_REQUEST_CMD, None)
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key

    def encode(self):
        return [self.cmd, self.key.encode(), 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]


class DKMColorResponsePacket(DuMangPacket):

    def __init__(self, red, green, blue):
        super().__init__(DKM_COLOR_RESPONSE_CMD, None)
        self.red = red
        self.green = green
        self.blue = blue

    @classmethod
    def fromrawbytes(cls, rawbytes):
        # TODO: It's possible the key is encoded in this packet type.
        return cls(rawbytes[3], rawbytes[4], rawbytes[5])

    def __repr__(self):
        return "{} - CMD:{:02X} Color: ({}, {}, {})".format(
            self.__class__.__name__, self.cmd, self.red, self.green, self.blue)


class DKMColorConfigurePacket(DuMangPacket):

    def __init__(self, key, red, green, blue):
        super().__init__(DKM_COLOR_CONFIGURE_CMD, None)
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key
        # NOTE: LEDs can only encode 4bits of color per channel.
        self.red = red % 16
        self.green = green % 16
        self.blue = blue % 16

    def encode(self):
        return [
            self.cmd,
            self.key.encode(), 0x00, self.red, self.green, self.blue
        ]


def signal_handler(signal, frame):
    sys.exit(0)


def initialize_devices():
    init_devices = []

    device_list = hid.enumerate(VENDOR_ID, PRODUCT_ID)

    ctrl_device = []
    for d in device_list:
        if d["interface_number"] == 1:
            ctrl_device.append(d)

    for d in ctrl_device:
        try:
            h = hid.device()
            h.open_path(d["path"])
            b = DuMangBoard(d["serial_number"], h)
            init_devices.append(b)

        except OSError as ex:
            logger.error(ex, exc_info=True)
            logger.error("Likely permissions error.")
            sys.exit(1)

    return init_devices


class NoHotplugSupport(Exception):
    pass


class TooManyBoards(Exception):
    pass


class DetectedDevice:

    def __init__(self, handle, on_close):
        self._handle = handle
        self._on_close = on_close

    def __str__(self):
        return "USB Detected Device at " + str(self._handle.getDevice())

    def close(self):
        # Note: device may have already left when this method is called,
        # so catch USBErrorNoDevice around cleanup steps involving the device.
        try:
            self.on_close(self)
        except usb1.USBErrorNoDevice:
            pass
        self._handle.close()


class USBConnectionMonitor:
    """
    Manages the hotplug events.
    Monitors the arrival and departure of USB devices.
    """

    def __init__(self, vendor_id, product_id):
        self.context = usb1.USBContext()
        if not self.context.hasCapability(usb1.CAP_HAS_HOTPLUG):
            raise NoHotplugSupport(
                "Hotplug support is missing. Please update your libusb version."
            )
        self._device_dict = {}
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.notify_q = queue.Queue()
        self._notify_threshold = 2
        self._has_started = False

    def _on_device_left(self, detected_device):
        logger.debug(f"Device left: {detected_device!s}")

    def _on_device_arrived(self, handle):
        detected_device = DetectedDevice(handle, self._on_device_left)
        logger.debug(f"Device arrived: {detected_device!s}")
        return detected_device

    def _register_callback(self):
        self._callback_handle = self.context.hotplugRegisterCallback(
            self._on_hotplug_event,
            events=usb1.HOTPLUG_EVENT_DEVICE_ARRIVED
            | usb1.HOTPLUG_EVENT_DEVICE_LEFT,
            vendor_id=self.vendor_id,
            product_id=self.product_id,
        )

    def _deregister_callback(self):
        self.context.hotplugDeregisterCallback(self._callback_handle)

    def _on_hotplug_event(self, context, device, event):
        if event == usb1.HOTPLUG_EVENT_DEVICE_LEFT:
            device_from_event = self._device_dict.pop(device, None)
            if device_from_event is not None:
                device_from_event.close()
            self._update_status()
            return
        try:
            handle = device.open()
        except usb1.USBError as ex:
            logger.error(ex, exc_info=True)
            return
        self._device_dict[device] = self._on_device_arrived(handle)
        self._update_status()

    def _update_status(self):
        total_connected = len(self._device_dict)
        if total_connected == self._notify_threshold:
            self._has_started = True
            self.ready()
        elif total_connected < self._notify_threshold:
            if self._has_started:
                self.wait()
        else:
            raise TooManyBoards(
                "Too many boards connected. Not sure how to handle it.")

    def ready(self):
        self.notify_q.put(NOTIFY_STATUS_READY)

    def wait(self):
        self.notify_q.put(NOTIFY_STATUS_WAIT)

    def get_status(self):
        return self.notify_q.get()

    def stop(self):
        self._deregister_callback()
        self.notify_q.put(NOTIFY_STATUS_STOP)

    def join(self):
        pass


class USBConnectionMonitorRunner(USBConnectionMonitor):
    """
    API: USB-event-centric application.
    Simplest API, for userland drivers which only react to USB events.
    """

    def __init__(self, vendor_id, product_id):
        super().__init__(vendor_id, product_id)
        self._observer = threading.Thread(target=self._run, daemon=True)
        self._shutdown_flag = threading.Event()

    def _run(self):
        with self.context:
            logger.debug("Registering hotplug callback...")
            self._register_callback()
            while not self._shutdown_flag.is_set():
                # NOTE: This call will block until callback is deregistered.
                self.context.handleEvents()

    def start(self):
        self._observer.start()

    def join(self):
        if self._observer:
            self._observer.join()

    def stop(self):
        if self._observer:
            # NOTE: Set shutdown_flag before stopping.
            self._shutdown_flag.set()
            super().stop()
