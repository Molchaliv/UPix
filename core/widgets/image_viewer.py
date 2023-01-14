from .image import QImageScene

from PySide6.QtCore import Qt, QPoint, QSize, QTimer
from PySide6.QtGui import QPixmap, QPainter, QMouseEvent, QWheelEvent, QResizeEvent
from PySide6.QtWidgets import QGraphicsView


def get_factors(width: int, height: int):
    return 1.1 ** (width // 100), (1 / 1.1) ** (height // 100)


def get_factors_beta(pixmap_size: QSize, widget_size: QSize):
    if pixmap_size.width() > widget_size.width() and pixmap_size.height() > widget_size.height():
        if pixmap_size.width() / pixmap_size.height() > widget_size.width() / widget_size.height():
            return 1.1 ** (pixmap_size.width() // 100), 1 / (widget_size.height() / pixmap_size.height())
        else:
            return 1.1 ** (pixmap_size.width() // 100), 1 / (widget_size.width() / pixmap_size.width())

    return 1.1 ** (pixmap_size.width() // 100), 1


def get_scale(pixmap_size: QSize, widget_size: QSize):
    factor = 1
    if pixmap_size.width() > widget_size.width() or pixmap_size.height() > widget_size.height():
        while pixmap_size.width() * factor > widget_size.width() or \
                pixmap_size.height() * factor > widget_size.height():
            factor *= (1 / 1.006)

    return factor


class QGraphicsImageView(QGraphicsView):
    def __init__(self, *args, **kwargs):
        super(QGraphicsImageView, self).__init__(*args, **kwargs)

        self._rotation = 0
        self._animation = None

        self._scale_factor = 1
        self._adjust_factor = 1
        self._max_factor = 1.1 ** 10
        self._min_factor = (1 / 1.1) ** 10

        self._rotate_factor = 0
        self._flip_h = False
        self._flip_v = False

        self.scene = QImageScene(self)

        self.setScene(self.scene)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.setFrameShape(QGraphicsView.Shape.NoFrame)
        self.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform | QPainter.RenderHint.Antialiasing)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.NoAnchor)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.NoAnchor)

    def transforms(self):
        return {
            "rotate": self._rotate_factor,
            "flip_h": self._flip_h,
            "flip_v": self._flip_v
        }

    def setTransforms(self, transforms: dict):
        self.rotate(transforms["rotate"])

        if transforms["flip_h"]:
            self.flipHorizontal()
        if transforms["flip_v"]:
            self.flipVertical()

    def setPixmap(self, pixmap: QPixmap):
        self.scene.setPixmap(pixmap)

        self._scale_factor = get_scale(pixmap.size(), self.parent().size())
        self._adjust_factor = self._scale_factor
        self._max_factor, self._min_factor = get_factors(
            pixmap.width(), pixmap.height()
        )

        self._rotate_factor = 0
        self._flip_h = False
        self._flip_v = False

        self.resetTransform()
        self.centerOn(self.items()[0])
        self.scale(self._scale_factor, self._scale_factor)

    def flipVertical(self):
        self._flip_v = not self._flip_v

        self.scale(1, -1)

    def flipHorizontal(self):
        self._flip_h = not self._flip_h

        self.scale(-1, 1)

    def rotate(self, angle: float):
        self._rotate_factor += angle

        super(QGraphicsImageView, self).rotate(angle)

    def rotate90(self, animate: bool = False):
        if animate:
            if not self._animation:
                self._rotation = 0

                self._animation = QTimer(self)
                self._animation.timeout.connect(self._rotate_fragment_90)
                self._animation.start(1)
        else:
            self.rotate(90)

    def _rotate_fragment_90(self):
        self.rotate(1)

        self._rotation += 1
        if self._rotation >= 90:
            self._animation = self._animation.stop()

    def zoom(self, angle: int):
        if angle > 0 and self._scale_factor <= self._max_factor:
            factor = 1.1
        elif angle < 0 and self._scale_factor >= self._min_factor:
            factor = (1 / 1.1)
        else:
            return False

        self._scale_factor *= factor

        self.scale(factor, factor)
        self.centerOn(self.items()[0])

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self._scale_factor = get_scale(self.scene.pixmap().size(), self.parent().size())
        self._adjust_factor = self._scale_factor

        self.resetTransform()
        self.centerOn(self.items()[0])
        self.scale(self._scale_factor, self._scale_factor)

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() == Qt.KeyboardModifier.NoModifier:
            old_pos = self.mapToScene(QPoint(
                int(event.position().x()), int(event.position().y())
            ))

            if not self.zoom(event.angleDelta().y()) is False:
                self.translate(
                    *(self.mapToScene(
                        int(event.position().x()),
                        int(event.position().y())) - old_pos
                      ).toTuple()
                )
        else:
            super(QGraphicsImageView, self).wheelEvent(event)

    def resizeEvent(self, event: QResizeEvent):
        if self._scale_factor == self._adjust_factor:
            self.scale(1 / self._scale_factor, 1 / self._scale_factor)

            self._scale_factor = get_scale(self.scene.pixmap().size(), self.parent().size())
            self._adjust_factor = self._scale_factor

            self.centerOn(self.items()[0])
            self.scale(self._scale_factor, self._scale_factor)

        return super(QGraphicsImageView, self).resizeEvent(event)
