from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QMouseEvent
from PySide6.QtWidgets import QToolButton


class QExtendedToolButton(QToolButton):
    rightClicked = Signal()

    def __init__(self, *args, **kwargs):
        super(QExtendedToolButton, self).__init__(*args, **kwargs)

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.RightButton:
            self.rightClicked.emit()

        return super(QExtendedToolButton, self).mousePressEvent(event)
