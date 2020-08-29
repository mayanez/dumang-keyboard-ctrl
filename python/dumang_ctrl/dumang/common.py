import hid
import sys
import signal
import queue
import threading
import logging
import usb1

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())

INIT_CMD = 0x30
SYNC_CMD = 0x46
INFO_CMD = 0x18
LAYER_PRESS_CMD = 0x3E
LAYER_DEPRESS_CMD = 0x3C
LIGHT_PULSE_CMD = 0x2A
KEY_REPORT_REQUEST_CMD = 0x04
KEY_REPORT_RESPONSE_CMD = 0x05
KEY_CONFIGURE_CMD = 0x09

VENDOR_ID = 0x0483
PRODUCT_ID = 0x5710
KBD_1_ID = 0x25
KBD_2_ID = 0x0D

MAX_KEYS = 256
UNKNOWN_KEYCODE_STR = "UNKNOWN"

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
    LAYER_TOGGLE_3 = 0xD6
    """Change while pressing to keyboard Layer 3"""

    LAYER_KEY_0 = 0xDC
    """Change when long pressing to keyboard Layer 0""" 
    LAYER_KEY_1 = 0xDD
    """Change when long pressing to keyboard Layer 1""" 
    LAYER_KEY_2 = 0xDE
    """Change when long pressing to keyboard Layer 2""" 
    LAYER_KEY_3 = 0xDF
    """Change when long pressing to keyboard Layer 3"""
    
    def __init__(self, keycode):
        self.keycode = keycode
        self.keystr = UNKNOWN_KEYCODE_STR

        for attribute in Keycode.__dict__.keys():
            if attribute[:2] != '__':
                value = getattr(Keycode, attribute)
                if not callable(value):
                    if self.keycode == value:
                        self.keystr = attribute

    def __lt__(self, other):
        return self.keycode < other.keycode

    def __eq__(self, other):
        return self.keycode == other.keycode

    def __hash__(self):
        return hash(self.keycode)

    @classmethod
    def fromstr(cls, keystr):
        for attribute in Keycode.__dict__.keys():
            if attribute[:2] != '__':
                value = getattr(Keycode, attribute)
                if not callable(value):
                    if keystr == attribute:
                        return cls(value)

    def encode(self):
        return self.keycode

    def __repr__(self):
        return "{}".format(self.keystr)

class Job(threading.Thread):
    def __init__(self, **kwargs):
        try:
            args = kwargs['args']
        except KeyError:
            args = []

        super().__init__(target=kwargs['target'], args=args, daemon=kwargs['daemon'])
        self.shutdown_flag = threading.Event()
        self.started = False

    def run(self):
        while not self.shutdown_flag.is_set():
            self._target(*self._args, **self._kwargs)
        logger.debug('Thread Killed')

    def start(self):
        if not self.started:
            self.started = True
            super().start()
        else:
            logger.debug('Thread previously started')

class JobKiller:
    def __init__(self):
        self.init = True

# TODO: Implement remaining packet types.
class DuMangKeyModule:
    def __init__(self, key, layer_keycodes=None):
        self.key = key
        self.layer_keycodes = layer_keycodes

    def __lt__(self, other):
        return self.key < other.key

    def __eq__(self, other):
        return self.key == other.key

    def __hash__(self):
        return hash(self.key)

    def encode(self):
        return self.key

    def __repr__(self):
        return "{:02X}".format(self.key) if isinstance(self.key, int) else "{}".format(self.key)

class DuMangBoard:
    READ_TIMEOUT_MS = 50

    def __init__(self, serial, handle):
        self.serial = serial
        self.handle = handle
        self._keys_initialized = False
        self._configured_keys = {}
        self.send_q = queue.Queue()
        self.recv_q = queue.Queue()

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

    def close(self):
        # NOTE: A hacky way of verifying if the handle is still valid.
        # I wonder if there is a cleaner way to do this.
        valid = True

        try:
            self.handle.read(64, timeout_ms=DuMangBoard.READ_TIMEOUT_MS)
        except OSError:
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

    def receive_thread(self):
        p = self.read_packet()

        if p:
            logger.debug(p)
            self.recv_q.put(p)

    def send_thread(self):
        p = self.send_q.get()

        # NOTE: Allows for thread to be killed with blocking queue
        if isinstance(p, JobKiller):
            sys.exit(0)

        self.write_packet(p)

    def configured_key(self, k):
        if self._keys_initialized:
            return self._configured_keys[k]

    @property
    def configured_keys(self):
        if not self._keys_initialized:
            for k in range(MAX_KEYS):
                self.put(KeyReportRequestPacket(k))

            while True:
                # NOTE: Wait for all requests to be sent out and the recv queue to be populated.
                if self.send_q.empty():
                    while not self.recv_q.empty():
                        p = self.recv_q.get()
                        if isinstance(p, KeyReportResponsePacket):
                            for l, kc in p.layer_keycodes.items():
                                if kc.keystr is not UNKNOWN_KEYCODE_STR:
                                    # NOTE: We add the layer_keycodes to the DKM
                                    p.key.layer_keycodes = p.layer_keycodes
                                    self._configured_keys[p.key.key] = p.key
                    self._keys_initialized = True
                    break

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
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return cls(True if rawbytes[2] == 0x03 else False, rawbytes[1])

    def encode(self):
        return [self.cmd, self.key.encode(), self.onoff, 0x0F, 0x0F, 0x0F]

class KeyReportRequestPacket(DuMangPacket):
    def __init__(self, key):
        super().__init__(KEY_REPORT_REQUEST_CMD, None)
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key

    def encode(self):
        return [self.cmd, self.key.encode(), 0x00, 0x00, 0x00]

class KeyReportResponsePacket(DuMangPacket):
    def __init__(self, key, layer_keycodes):
        super().__init__(KEY_REPORT_RESPONSE_CMD, None)
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key
        self.layer_keycodes = layer_keycodes

    @classmethod
    def fromrawbytes(cls, rawbytes):
        return cls(rawbytes[1], {0: Keycode(rawbytes[7]), 1: Keycode(rawbytes[8]), 2: Keycode(rawbytes[9]), 3: Keycode(rawbytes[10])})

    def __repr__(self):
        return "{} - CMD:{:02X} Key:{} LayerKeycodes:{}".format(self.__class__.__name__, self.cmd, self.key, self.layer_keycodes)

class KeyConfigurePacket(DuMangPacket):
    def __init__(self, key, layer_keycodes):
        super().__init__(KEY_CONFIGURE_CMD, None)
        self.key = DuMangKeyModule(key) if isinstance(key, int) else key
        self.layer_keycodes = {k: v.encode() if isinstance(v, Keycode) else v for k, v in layer_keycodes.items()}

    def encode(self):
        return [self.cmd, 0x01, self.layer_keycodes[1], self.layer_keycodes[2], self.layer_keycodes[3], 0xFF, self.layer_keycodes[0]]

    def __repr__(self):
        return "{} - CMD:{:02X} Key:{} LayerKeycodes:{}".format(self.__class__.__name__, self.cmd, self.key, self.layer_keycodes)

def signal_handler(signal, frame):
    sys.exit(0)

def initialize_devices():
    init_devices = []

    device_list = hid.enumerate(VENDOR_ID, PRODUCT_ID)

    ctrl_device = []
    for d in device_list:
        # TODO: Is there some way to check version of firmware?
        if d['interface_number'] == 1:
            ctrl_device.append(d)

    for d in ctrl_device:
        try:
            h = hid.device()
            h.open_path(d['path'])
            b = DuMangBoard(d['serial_number'], h)
            b.write_packet(InitializationPacket())
            init_devices.append(b)

        except IOError as ex:
            # TODO: Better error handling.
            logger.error(ex, exc_info=True)
            logger.error("Likely permissions error.")

    return init_devices

class NoHotplugSupport(Exception):
    pass

class TooManyBoards(Exception):
    pass

class DetectedDevice(object):
    onClose = lambda device: None

    def __init__(self, handle):
        self._handle = handle

    def __str__(self):
        # For demonstration purposes only.
        return 'USB Detected Device at ' + str(self._handle.getDevice())

    def close(self):
        # Note: device may have already left when this method is called,
        # so catch USBErrorNoDevice around cleanup steps involving the device.
        try:
            self.onClose(self)
            # Put device in low-power mode, release claimed interfaces...
            pass
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
                'Hotplug support is missing. Please update your libusb version.'
            )
        self._device_dict = {}
        self.vendor_id = vendor_id
        self.product_id = product_id
        self.notify_q = queue.Queue()
        self._notify_threshold = 2
        self._has_started = False

    def _on_device_left(self, detected_device):
        print('Device left:', str(detected_device))

    def _on_device_arrived(self, detected_device):
        detected_device.onClose = self._on_device_left
        print('Device arrived:', str(detected_device))

    def _register_callback(self):
        self.context.hotplugRegisterCallback(
            self._on_hotplug_event,
            # Just in case more events are added in the future.
            events=usb1.HOTPLUG_EVENT_DEVICE_ARRIVED | usb1.HOTPLUG_EVENT_DEVICE_LEFT,
            # Edit these if you handle devices from a single vendor, of a
            # single product type or of a single device class; and simplify
            # device filtering accordingly in _on_hotplug_event.
            vendor_id=self.vendor_id,
            product_id=self.product_id,
            #dev_class=,
        )

    def _on_hotplug_event(self, context, device, event):
        if event == usb1.HOTPLUG_EVENT_DEVICE_LEFT:
            device_from_event = self._device_dict.pop(device, None)
            self._update_status()
            if device_from_event is not None:
                device_from_event.close()
            return
        try:
            handle = device.open()
        except usb1.USBError:
            return
        detected_device = DetectedDevice(handle)
        if self._on_device_arrived(detected_device):
            detected_device.close()
            return
        self._device_dict[device] = detected_device
        self._update_status()
    
    def _update_status(self):
        total_connected = len(self._device_dict)
        if total_connected == self._notify_threshold:
            self._has_started = True
            self.ready()
        elif total_connected < self._notify_threshold:
            if(self._has_started):
                self.wait()
        else:
            raise TooManyBoards(
                'Too many boards connected. Not sure how to handle it.'
            )


    def ready(self):
        self.notify_q.put('ready')
    
    def wait(self):
        self.notify_q.put('wait')

    def get_status(self):
        return self.notify_q.get()

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


    def _run(self):
        with self.context:
            print('Registering hotplug callback...')
            self._register_callback()
            while True:
                self.context.handleEvents()

    def start(self):
        self._observer.start()
    
    def join(self):
        if self._observer:
            self._observer.join()