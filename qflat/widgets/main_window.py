from PySide6.QtCore import Qt, QSize

from pyqt_frameless_window import FramelessMainWindow

from PySide6.QtGui import QIcon, QResizeEvent, QMouseEvent
from PySide6.QtWidgets import QToolButton


class QCustomizeWindow(FramelessMainWindow):
    def __init__(self):
        super(QCustomizeWindow, self).__init__()

        self.setStyleSheet("QCustomizeWindow { background: #202020; }")

        self._close_button = QToolButton(self)
        self._close_button.setIconSize(QSize(10, 10))
        self._close_button.resize(46, 32)
        self._close_button.setIcon(QIcon(r"C:\Users\Никита\Downloads\title_bar_icons\close.png"))
        self._close_button.setStyleSheet("QToolButton { background: transparent; border: none; border-radius: 0px; }"
                                         "QToolButton:hover { background: #E80000; }"
                                         "QToolButton:pressed { background: #E60000; }")
        self._close_button.clicked.connect(self.close)

        self._maximize_button = QToolButton(self)
        self._maximize_button.setIconSize(QSize(10, 10))
        self._maximize_button.resize(46, 32)
        self._maximize_button.setIcon(QIcon(r"C:\Users\Никита\Downloads\title_bar_icons\maximize.png"))
        self._maximize_button.setStyleSheet("QToolButton { background: transparent; border: none; border-radius: 0px; }"
                                            "QToolButton:hover { background: #303030; }"
                                            "QToolButton:pressed { background: #323232; }")
        self._maximize_button.clicked.connect(self.restoreMaximize)

        self._minimize_button = QToolButton(self)
        self._minimize_button.setIconSize(QSize(11, 11))
        self._minimize_button.resize(46, 32)
        self._minimize_button.setIcon(QIcon(r"C:\Users\Никита\Downloads\title_bar_icons\minimize.png"))
        self._minimize_button.setStyleSheet("QToolButton { background: transparent; border: none; border-radius: 0px; }"
                                            "QToolButton:hover { background: #303030; }"
                                            "QToolButton:pressed { background: #323232; }")
        self._minimize_button.clicked.connect(self.showMinimized)

    def restoreMaximize(self):
        if self.isMaximized():
            self.showNormal()
        else:
            self.showMaximized()

        self.updateRestoreMaximizeButton()

    def showFullScreen(self):
        self._close_button.hide()
        self._maximize_button.hide()
        self._minimize_button.hide()

        super(QCustomizeWindow, self).showFullScreen()

    def showNormal(self):
        if self.isFullScreen():
            self._close_button.show()
            self._maximize_button.show()
            self._minimize_button.show()

        super(QCustomizeWindow, self).showNormal()

    def setWindowState(self, state: Qt.WindowState):
        super(QCustomizeWindow, self).setWindowState(state)

        if self.isFullScreen():
            self._close_button.hide()
            self._maximize_button.hide()
            self._minimize_button.hide()
        else:
            self._close_button.show()
            self._maximize_button.show()
            self._minimize_button.show()

    def updateRestoreMaximizeButton(self):
        if self.isMaximized():
            self._maximize_button.setIcon(QIcon(r"C:\Users\Никита\Downloads\title_bar_icons\restore.png"))
        else:
            self._maximize_button.setIcon(QIcon(r"C:\Users\Никита\Downloads\title_bar_icons\maximize.png"))

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.updateRestoreMaximizeButton()

        super(QCustomizeWindow, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        if event.y() <= 32:
            self.restoreMaximize()

    def eventFilter(self, watched, event):
        super(QCustomizeWindow, self).eventFilter(watched, event)

        self.update()

    def resizeEvent(self, event: QResizeEvent):
        self._close_button.move(event.size().width() - 46, 0)
        self._maximize_button.move(event.size().width() - 92, 0)
        self._minimize_button.move(event.size().width() - 138, 0)

        self.updateRestoreMaximizeButton()
