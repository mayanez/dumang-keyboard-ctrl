import sys

from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QComboBox, QVBoxLayout, QWidget, QLabel
from collections import defaultdict
from dumang_common import *

pulse_onoff = defaultdict(lambda: False)

def on_pulse_click(kbd, key):
    pulse_onoff[key] = not pulse_onoff[key]
    p = LightPulsePacket(pulse_onoff[key], DuMangKeyModule(int(key)))
    kbd.put(p)

def on_keys_combobox_change(kbd, key, layer0_label, layer1_label, layer2_label, layer3_label):
    dkm = kbd.configured_key(int(key))
    layer0_label.setText(str(dkm.layer_keycodes[0]))
    layer1_label.setText(str(dkm.layer_keycodes[1]))
    layer2_label.setText(str(dkm.layer_keycodes[2]))
    layer3_label.setText(str(dkm.layer_keycodes[3]))

def inspect_gui(kbd1, kbd2):
    app = QApplication([])
    window = QMainWindow()
    central = QWidget()
    layout = QVBoxLayout()

    # TODO: How to consolidate all this?
    kbd1_label = QLabel("KBD: " + kbd1.serial)
    kbd2_label = QLabel("KBD: " + kbd2.serial)

    layer0_label = QLabel("")
    layer1_label = QLabel("")
    layer2_label = QLabel("")
    layer3_label = QLabel("")

    layer0_label2 = QLabel("")
    layer1_label2 = QLabel("")
    layer2_label2 = QLabel("")
    layer3_label2 = QLabel("")

    keys_combobox = QComboBox()
    pulse_button = QPushButton("Pulse Toggle")

    for k in kbd1.configured_keys:
        keys_combobox.addItem(str(k))

    layout.addWidget(kbd1_label)
    layout.addWidget(keys_combobox)
    layout.addWidget(layer0_label)
    layout.addWidget(layer1_label)
    layout.addWidget(layer2_label)
    layout.addWidget(layer3_label)
    layout.addWidget(pulse_button)

    keys_combobox2 = QComboBox()
    pulse_button2 = QPushButton("Pulse Toggle")

    for k in kbd2.configured_keys:
        keys_combobox2.addItem(str(k))

    layout.addWidget(kbd2_label)
    layout.addWidget(keys_combobox2)
    layout.addWidget(layer0_label2)
    layout.addWidget(layer1_label2)
    layout.addWidget(layer2_label2)
    layout.addWidget(layer3_label2)
    layout.addWidget(pulse_button2)

    central.setLayout(layout)

    # Initialize
    on_keys_combobox_change(kbd1, keys_combobox.currentText(), layer0_label, layer1_label, layer2_label, layer3_label)
    on_keys_combobox_change(kbd2, keys_combobox2.currentText(), layer0_label2, layer1_label2, layer2_label2, layer3_label2)

    keys_combobox.currentTextChanged.connect(lambda x: on_keys_combobox_change(kbd1, x, layer0_label, layer1_label, layer2_label, layer3_label))
    pulse_button.clicked.connect(lambda : on_pulse_click(kbd1, keys_combobox.currentText()))

    keys_combobox2.currentTextChanged.connect(lambda x: on_keys_combobox_change(kbd2, x, layer0_label2, layer1_label2, layer2_label2, layer3_label2))
    pulse_button2.clicked.connect(lambda : on_pulse_click(kbd2, keys_combobox2.currentText()))

    window.setCentralWidget(central)
    window.show()
    sys.exit(app.exec_())
