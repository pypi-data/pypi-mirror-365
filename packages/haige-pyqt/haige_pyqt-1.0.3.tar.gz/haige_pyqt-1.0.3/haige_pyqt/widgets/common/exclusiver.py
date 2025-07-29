from __future__ import annotations

import sys

from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QToolButton, QAction, QPushButton


class ExclusiveCheckedGroup(QObject):
    on_checked_change = pyqtSignal(bool, QObject)

    def __init__(self, items: [QAction | QToolButton | QPushButton] = None, allow_empty_checked=True, parent=None):
        super().__init__(parent)
        self._items = []
        self.add(items)
        self._allow_empty_checked = allow_empty_checked

    def add(self, items: [QAction | QToolButton | QPushButton]):
        if not items:
            return
        for item in items:
            if item not in self._items:
                item.setCheckable(True)
                item.toggled.connect(self._toggled)
                self._items.append(item)

    def remove(self, items: [QAction | QToolButton | QPushButton]):
        if not items:
            return
        for item in items:
            if item not in self._items:
                continue
            item.toggled.disconnect(self._toggled)
            self._items.remove(item)

    def _toggled(self, checked):
        has_checked = False
        sender = self.sender()
        if checked:
            for item in self._items:
                if item != sender:
                    item.setChecked(False)
        for ac in self._items:
            if ac.isChecked():
                has_checked = True
                break
        # 如果不允许空白选中（也就是必须要有一个选中，那 sender 就不能被设置为非选中状态）
        if not self._allow_empty_checked and not has_checked:
            has_checked = True
            sender.setChecked(True)
        self.on_checked_change.emit(has_checked, sender)


if __name__ == '__main__':
    from PyQt5.QtWidgets import QApplication, QMainWindow, QHBoxLayout, QFrame, QToolBar


    def _handle_on_checked_change(obj, sender):
        print(sender, sender.text(), obj)


    app = QApplication(sys.argv)
    main = QMainWindow()
    mainFram = QFrame()
    layout = QHBoxLayout(mainFram)
    mainFram.setLayout(layout)
    main.setCentralWidget(mainFram)

    ac1 = QAction(text="ac1")
    ac2 = QAction(text="ac2")
    ac3 = QAction(text="ac3")
    toolbar = QToolBar(main)
    toolbar.addAction(ac1)
    toolbar.addAction(ac2)
    toolbar.addAction(ac3)
    layout.addWidget(toolbar)
    ac_exclusive = ExclusiveCheckedGroup([ac1, ac2, ac3])
    ac_exclusive.on_checked_change.connect(_handle_on_checked_change)

    btn1 = QPushButton(text="btn1")
    btn2 = QPushButton(text="btn2")
    btn3 = QPushButton(text="btn3")
    layout.addWidget(btn1)
    layout.addWidget(btn2)
    layout.addWidget(btn3)
    ac_exclusive2 = ExclusiveCheckedGroup([btn1, btn2, btn3])
    ac_exclusive2.on_checked_change.connect(_handle_on_checked_change)

    tb1 = QToolButton(text="tb1")
    tb2 = QToolButton(text="tb2")
    tb3 = QToolButton(text="tb3")
    layout.addWidget(tb1)
    layout.addWidget(tb2)
    layout.addWidget(tb3)
    ac_exclusive3 = ExclusiveCheckedGroup([tb1, tb2, tb3])
    ac_exclusive3.on_checked_change.connect(_handle_on_checked_change)

    bt001 = QPushButton(text="must has on checked 01")
    tb001 = QToolButton(text="must has on checked 02")
    layout.addWidget(bt001)
    layout.addWidget(tb001)
    ac_exclusive_not_allow_empty_checked = ExclusiveCheckedGroup([bt001, tb001], allow_empty_checked=False)
    ac_exclusive_not_allow_empty_checked.on_checked_change.connect(_handle_on_checked_change)

    main.show()
    sys.exit(app.exec_())
