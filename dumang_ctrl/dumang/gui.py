import sys

from PyQt6 import uic, QtGui
from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from collections import defaultdict
from .common import *


class KBDTableView(QTableWidget):
    itemLeave = pyqtSignal()

    HEADERS = ['Keycode', 'Layer 0', 'Layer 1', 'Layer 2', 'Layer 3']

    def __init__(self, keys, *args):
        super().__init__(len(keys), len(KBDTableView.HEADERS), *args)
        self.keys = keys
        self.setData()
        self.resizeColumnsToContents()
        self.resizeRowsToContents()
        self._last_item = None
        self.viewport().installEventFilter(self)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.setSelectionBehavior(QTableView.SelectRows)

    def setData(self):
        for n, p in enumerate(self.keys.items()):
            kc, k = p

            for m, layer in enumerate(k.layer_keycodes.values()):
                newitem = QTableWidgetItem(str(layer))
                newitem.setFlags(Qt.ItemIsEnabled)
                newitem.setFlags(Qt.ItemFlag.ItemIsEnabled)
                self.setItem(n, m + 1, newitem)

            keycodeitem = QTableWidgetItem(str(hex(kc)))
            keycodeitem.setFlags(Qt.ItemIsEnabled)
            keycodeitem.setFlags(Qt.ItemFlag.ItemIsEnabled)
            self.setItem(n, 0, keycodeitem)

        self.setHorizontalHeaderLabels(KBDTableView.HEADERS)

    def eventFilter(self, widget, event):
        if widget is self.viewport():
            if event.type() == QEvent.Type.Leave:
                index = QModelIndex()
                self.itemLeave.emit()
                return True

        return QTableWidget.eventFilter(self, widget, event)

    def _on_itemEntered(self, kbd, item):
        # NOTE: The lack of itemLeave/Exited requires us to track last item.
        # Previous solution as descriped in https://stackoverflow.com/questions/20064975
        # proved problematic when scrolling as it would trigger Enter events, but no Leave events.
        if item != self._last_item and self._last_item is not None:
            p = LightPulsePacket(
                False,
                self.keys[int(self.item(self._last_item.row(), 0).data(0),
                              16)].key)
            kbd.put(p)

        p = LightPulsePacket(
            True, self.keys[int(self.item(item.row(), 0).data(0), 16)].key)
        kbd.put(p)
        self._last_item = item

    def _on_itemLeave(self, kbd):
        p = LightPulsePacket(
            False,
            self.keys[int(self.item(self._last_item.row(), 0).data(0),
                          16)].key)
        kbd.put(p)


class KBDWidget(QWidget):

    def __init__(self, parent, kbd):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.tableWidget = self._add_table_widget(kbd)
        self.layout.addWidget(self.tableWidget)
        self.setLayout(self.layout)

    def _add_table_widget(self, kbd):
        kbd_widget = KBDTableView(kbd.configured_keys)
        kbd_widget.setMouseTracking(True)
        kbd_widget.itemEntered.connect(
            lambda item: kbd_widget._on_itemEntered(kbd, item))
        kbd_widget.itemLeave.connect(lambda: kbd_widget._on_itemLeave(kbd))
        return kbd_widget

    def hideLayout(self, n):
        self.tableWidget.hideColumn(n + 1)

    def showLayout(self, n):
        self.tableWidget.showColumn(n + 1)


class KBDTab(QWidget):

    def __init__(self, parent, kbd):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.kbd_label = QLabel("KBD: " + kbd.serial)
        self.layout.addWidget(self.kbd_label)

        # Add dropdown/combo box
        headers = [f'Layer {i}' for i in range(MAX_LAYERS)]
        self.comboLayouts = QComboBox()
        self.comboLayouts.addItems(headers)
        self.label = QLabel("&L:")
        self.label.setBuddy(self.comboLayouts)
        self.layout.addWidget(self.comboLayouts)

        self.comboLayouts.currentIndexChanged.connect(self.changeKBDLayout)
        self.kbdWidget = KBDWidget(self, kbd)
        self.layout.addWidget(self.kbdWidget)
        self.comboLayouts.setCurrentIndex(0)
        self.changeKBDLayout()

    def changeKBDLayout(self):
        show = self.comboLayouts.currentIndex()
        hide = [x for x in range(5) if x != show]
        list(map(lambda x: self.kbdWidget.hideLayout(x), hide))
        self.kbdWidget.showLayout(show)


class KBDTabs(QWidget):

    def __init__(self, parent, kbds):
        super(QWidget, self).__init__(parent)
        self.layout = QVBoxLayout(self)

        # Initialize tab screen
        self.tabs = QTabWidget()
        # Add tabs
        for i, kbd in enumerate(kbds):
            self.tabs.addTab(KBDTab(self, kbd), f'Board {i}')
        self.tabs.resize(300, 200)

        # Add tabs to widget
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

    @pyqtSlot()
    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            print(currentQTableWidgetItem.row(),
                  currentQTableWidgetItem.column(),
                  currentQTableWidgetItem.text())


class App(QMainWindow):

    def __init__(self):
        super().__init__()
        self.title = 'Dumang Board Progamming Tool'
        self.left = 0
        self.top = 0
        self.width = 500
        self.height = 500
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.center()

    def center(self):
        pass
        centerPoint = QtGui.QGuiApplication.primaryScreen().availableGeometry(
        ).center()
        self.move(centerPoint - self.frameGeometry().center())


def inspect_gui(kbd1, kbd2=None):
    init = QApplication([])
    app = App()
    kbds = [kbd for kbd in [kbd1, kbd2] if kbd is not None]
    app.setCentralWidget(KBDTabs(app, kbds))
    app.show()
    sys.exit(init.exec())
