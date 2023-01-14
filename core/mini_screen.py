from .widgets import QExtendedToolButton

from PySide6.QtCore import Qt, QPoint, QSize
from PySide6.QtGui import QPixmap, QResizeEvent, QMouseEvent
from PySide6.QtWidgets import QWidget, QFrame, QLabel


class QWidgetStub(QWidget):
    theme_path: str = ""


class QCloseButton(QExtendedToolButton):
    def __init__(self, *args, **kwargs):
        super(QCloseButton, self).__init__(*args, **kwargs)


class QMiniScreen(QWidget):
    def __init__(self, parent: QWidget | QWidgetStub, pixmap: QPixmap):
        super(QMiniScreen, self).__init__()

        self._old_pos = QPoint(0, 0)

        self._factor_wh = pixmap.width() / pixmap.height()
        self._factor_hw = pixmap.height() / pixmap.width()

        self._frame = QFrame(self)

        self._image = QLabel(self)
        self._image.setScaledContents(True)
        self._image.setPixmap(pixmap)

        self._close = QCloseButton(self)
        self._close.setIcon(QPixmap(f"{parent.theme_path}\\close.png"))
        self._close.setIconSize(QSize(20, 20))
        self._close.resize(QSize(30, 30))
        self._close.clicked.connect(self.close)

        self.setMinimumSize(200, 150)
        self.setWindowFlags(
            Qt.WindowType.CustomizeWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )

    def setPixmap(self, pixmap: QPixmap):
        self._image.setPixmap(pixmap)

    def mousePressEvent(self, event: QMouseEvent):
        self._old_pos = QPoint(event.x(), event.y())

    def mouseMoveEvent(self, event: QMouseEvent):
        self.move(
            int(event.screenPos().x() - self._old_pos.x()),
            int(event.screenPos().y() - self._old_pos.y())
        )

    def resizeEvent(self, event: QResizeEvent):
        if self._factor_wh < (event.size().width() / event.size().height()):
            self._image.resize(
                event.size().height() * self._factor_wh,
                event.size().height()
            )
        else:
            self._image.resize(
                event.size().width(),
                event.size().width() * self._factor_hw
            )

        self._frame.resize(event.size())
        self._close.move(event.size().width() - 40, 5)
        self._image.move(
            (self.width() // 2) - (self._image.width() // 2),
            (self.height() // 2) - (self._image.height() // 2)
        )
