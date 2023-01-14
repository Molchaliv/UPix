from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QGraphicsPixmapItem, QLabel


class QImageScene(QGraphicsScene):
    def __init__(self, *args, **kwargs):
        super(QImageScene, self).__init__(*args, **kwargs)

        # self.image = QLabel()
        # self.item = self.addWidget(self.image)

        self.item = QGraphicsPixmapItem()
        self.item.setTransformationMode(Qt.TransformationMode.SmoothTransformation)
        self.item.setCacheMode(QGraphicsPixmapItem.CacheMode.NoCache)
        self.item.setZValue(0)

        self.addItem(self.item)

    def pixmap(self):
        return self.item.pixmap()

    def setPixmap(self, pixmap: QPixmap):
        # self.image.setPixmap(pixmap)
        # self.image.move(0, 0)
        # self.image.resize(pixmap.size())

        self.item.setPixmap(pixmap)

        self.setSceneRect(0, 0, pixmap.width(), pixmap.height())
