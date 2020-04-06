import sys

from PyQt5 import uic, QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from collections import defaultdict
from .common import *

class KBDTableView(QTableWidget):
    cellExited = pyqtSignal(int, int)
    itemExited = pyqtSignal(QTableWidgetItem)

    HEADERS = ['Keycode', 'Layer 0', 'Layer 1', 'Layer 2', 'Layer 3']

    def __init__(self, keys, *args):
        super().__init__(len(keys), len(KBDTableView.HEADERS), *args)
        self.keys = keys
        self.setData()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self._last_index = QPersistentModelIndex()
        self.viewport().installEventFilter(self)

    def setData(self):
        for n, p in enumerate(self.keys.items()):
            kc, k = p

            for m, layer in enumerate(k.layer_keycodes.values()):
                newitem = QTableWidgetItem(str(layer))
                newitem.setFlags(Qt.ItemIsEnabled)
                self.setItem(n, m+1, newitem)

            keycodeitem = QTableWidgetItem(str(hex(kc)))
            keycodeitem.setFlags(Qt.ItemIsEnabled)
            self.setItem(n, 0, keycodeitem)

        self.setHorizontalHeaderLabels(KBDTableView.HEADERS)

    def eventFilter(self, widget, event):
        if widget is self.viewport():
            index = self._last_index
            if event.type() == QEvent.MouseMove:
                index = self.indexAt(event.pos())
            elif event.type() == QEvent.Leave:
                index = QModelIndex()
            if index != self._last_index:
                row = self._last_index.row()
                column = self._last_index.column()
                item = self.item(row, column)
                if item is not None:
                    self.itemExited.emit(item)
                self.cellExited.emit(row, column)
                self._last_index = QPersistentModelIndex(index)
        return QTableWidget.eventFilter(self, widget, event)

    def _on_itemEntered(self, kbd, item):
        p = LightPulsePacket(True, self.keys[int(self.item(item.row(), 0).data(0), 16)])
        kbd.put(p)

    def _on_itemExited(self, kbd, item):
        p = LightPulsePacket(False, self.keys[int(self.item(item.row(), 0).data(0), 16)])
        kbd.put(p)

def inspect_gui(kbd1, kbd2=None):
    app = QApplication([])
    window = QMainWindow()
    central = QWidget()
    layout = QVBoxLayout()

    kbd1_label = QLabel("KBD: " + kbd1.serial)
    layout.addWidget(kbd1_label)

    kbd1_widget = KBDTableView(kbd1.configured_keys)
    kbd1_widget.setMouseTracking(1)
    kbd1_widget.itemEntered.connect(lambda item: kbd1_widget._on_itemEntered(kbd1, item))
    kbd1_widget.itemExited.connect(lambda item: kbd1_widget._on_itemExited(kbd1, item))
    layout.addWidget(kbd1_widget)

    if kbd2:
        kbd2_label = QLabel("KBD: " + kbd2.serial)
        layout.addWidget(kbd2_label)

        kbd2_widget = KBDTableView(kbd2.configured_keys)
        kbd2_widget.setMouseTracking(1)
        kbd2_widget.itemEntered.connect(lambda item: kbd2_widget._on_itemEntered(kbd2, item))
        kbd2_widget.itemExited.connect(lambda item: kbd2_widget._on_itemExited(kbd2, item))
        layout.addWidget(kbd2_widget)

    central.setLayout(layout)

    window.setCentralWidget(central)
    window.show()
    sys.exit(app.exec_())
