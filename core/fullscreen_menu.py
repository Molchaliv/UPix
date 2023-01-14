from .widgets import QExtendedToolButton

from PySide6.QtCore import Qt, QSize, QPoint
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget


class QWidgetStub(QWidget):
    theme_path: str = ""


class QFullScreenMenu(QExtendedToolButton):
    def __init__(self, parent: QWidget | QWidgetStub = None):
        super(QFullScreenMenu, self).__init__(parent=parent)

        self._parent = parent

        self.setIcon(QPixmap(f"{parent.theme_path}\\full-screen.png"))
        self.setIconSize(QSize(20, 20))
        self.resize(30, 30)
        self.move(self.getPos())
        self.clicked.connect(self.showFullScreenOrMinimize)

    def getPos(self):
        return QPoint(self._parent.width() - 40, self._parent.height() - 40)

    def showFullScreenOrMinimize(self):
        if not self._parent.isFullScreen():
            self._parent.showFullScreen()

            self.setIcon(QPixmap(f"{self._parent.theme_path}\\minimize.png"))
        else:
            self._parent.showNormal()

            self.setIcon(QPixmap(f"{self._parent.theme_path}\\full-screen.png"))
