from .widgets import QExtendedToolButton, QExtendedMenu, QGraphicsImageView

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QSlider


class QWidgetStub(QWidget):
    theme_path: str = ""


class QRotateMenu(QExtendedMenu):
    def __init__(self, parent: QWidget | QWidgetStub, view: QGraphicsImageView):
        super(QRotateMenu, self).__init__(parent=parent)
        
        self._parent = parent
        self._view = view

        self._value = 0

        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Orientation.Horizontal)
        self.slider.setMinimum(-360)
        self.slider.setMaximum(360)
        self.slider.resize(125, 45)
        self.slider.move(10, 1)
        self.slider.valueChanged.connect(self.rotateImage)

        self.flip_v = QExtendedToolButton(self)
        self.flip_v.setIcon(QPixmap(f"{parent.theme_path}\\flip-vertical.png"))
        self.flip_v.setIconSize(QSize(20, 20))
        self.flip_v.move(145, 7)
        self.flip_v.resize(30, 30)
        self.flip_v.clicked.connect(self._view.flipVertical)

        self.flip_h = QExtendedToolButton(self)
        self.flip_h.setIcon(QPixmap(f"{parent.theme_path}\\flip-horizontal.png"))
        self.flip_h.setIconSize(QSize(20, 20))
        self.flip_h.move(175, 7)
        self.flip_h.resize(30, 30)
        self.flip_h.clicked.connect(self._view.flipHorizontal)

        self.exit = QExtendedToolButton(self)
        self.exit.setIcon(QPixmap(f"{parent.theme_path}\\close.png"))
        self.exit.setIconSize(QSize(20, 20))
        self.exit.move(210, 7)
        self.exit.resize(30, 30)
        self.exit.clicked.connect(self.hideMenu)

        self.resize(250, 45)
        self.move(self.getPos())

    def rotateImage(self):
        self._view.rotate(self.slider.value() - self._value)

        self._value = self.slider.value()

    def showMenu(self):
        super(QRotateMenu, self).showMenu()

        self.slider.setEnabled(True)
        self.slider.setValue(0)

    def hideMenu(self):
        super(QRotateMenu, self).hideMenu()

        self.slider.setEnabled(False)
