import sys

from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QComboBox, QVBoxLayout, QWidget, QLabel
from collections import defaultdict
from dumang_common import *

pulse_onoff = defaultdict(lambda: False)

def on_pulse_click(key, q, q2):
    print(key)
    pulse_onoff[key] = not pulse_onoff[key]
    print(pulse_onoff[key])
    p = LightPulsePacket(pulse_onoff[key], Keycode(int(key)).encode())
    # TODO: Send to proper half?
    q.put(p)
    q2.put(p)

def on_keys_combobox_change(key, q, q2, layer0_label, layer1_label, layer2_label, layer3_label):
    # TODO: Report current configuration.
    pass

def inspect_gui(q, q2):
    app = QApplication([])
    window = QMainWindow()
    central = QWidget()
    layout = QVBoxLayout()

    layer0_label = QLabel("")
    layer1_label = QLabel("")
    layer2_label = QLabel("")
    layer3_label = QLabel("")

    keys_combobox = QComboBox()
    pulse_button = QPushButton("Pulse Toggle")

    # TODO: Populate according to actually connected keys.
    for k in range(MAX_KEYS):
        keys_combobox.addItem(str(k))

    layout.addWidget(keys_combobox)
    layout.addWidget(layer0_label)
    layout.addWidget(layer1_label)
    layout.addWidget(layer2_label)
    layout.addWidget(layer3_label)
    layout.addWidget(pulse_button)

    central.setLayout(layout)

    keys_combobox.currentTextChanged.connect(lambda x: on_keys_combobox_change(x, q, q2, layer0_label, layer1_label, layer2_label, layer3_label))
    pulse_button.clicked.connect(lambda : on_pulse_click(keys_combobox.currentText(), q, q2))

    window.setCentralWidget(central)
    window.show()
    sys.exit(app.exec_())
