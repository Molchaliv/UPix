import os

from .widgets import QDropdownMenu, QGraphicsImageView, QExtendedToolButton

from .info_menu import QInfoMenu
from .mini_screen import QMiniScreen
from .rotate_menu import QRotateMenu

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImageReader, QShortcut, QKeySequence
from PySide6.QtWidgets import QWidget, QFileDialog, QApplication


class QWidgetStub(QWidget):
    theme_path: str = ""


class QMiniMenu(QDropdownMenu):
    def __init__(self, parent: QWidget | QWidgetStub, app: QApplication, view: QGraphicsImageView,
                 info_menu: QInfoMenu, rotate_menu: QRotateMenu):
        super(QMiniMenu, self).__init__(parent=parent)

        self._parent = parent
        self._app = app
        self._view = view
        self._info_menu = info_menu
        self._rotate_menu = rotate_menu

        self._mini_screen = None

        self._images = []
        self._transforms = {}
        self._current_index = -1

        if len(self._app.arguments()) >= 2:
            if os.path.exists(self._app.arguments()[1]):
                self.load_image(self._app.arguments()[1])

        self.back = QExtendedToolButton()
        self.back.setIcon(QPixmap(f"{self._parent.theme_path}\\back.png"))
        self.back.clicked.connect(self.back_image)
        self.back_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Left), self._parent)
        self.back_shortcut.activated.connect(self.back_image)

        self.next = QExtendedToolButton()
        self.next.setIcon(QPixmap(f"{self._parent.theme_path}\\next.png"))
        self.next.clicked.connect(self.next_image)
        self.next_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Right), self._parent)
        self.next_shortcut.activated.connect(self.next_image)

        self.zoom_in = QExtendedToolButton()
        self.zoom_in.setIcon(QPixmap(f"{self._parent.theme_path}\\zoom-in.png"))
        self.zoom_in.clicked.connect(self.zoom_in_func)
        self.zoom_in_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Up), self._parent)
        self.zoom_in_shortcut.activated.connect(self.zoom_in_func)

        self.zoom_out = QExtendedToolButton()
        self.zoom_out.setIcon(QPixmap(f"{self._parent.theme_path}\\zoom-out.png"))
        self.zoom_out.clicked.connect(self.zoom_out_func)
        self.zoom_out_shortcut = QShortcut(QKeySequence(Qt.Key.Key_Down), self._parent)
        self.zoom_out_shortcut.activated.connect(self.zoom_out_func)

        self.rotate = QExtendedToolButton()
        self.rotate.setIcon(QPixmap(f"{self._parent.theme_path}\\rotate.png"))
        self.rotate.clicked.connect(self.rotate_90)
        self.rotate.rightClicked.connect(self.rotate_menu)
        self.rotate_shortcut = QShortcut(QKeySequence(Qt.Key.Key_R), self._parent)
        self.rotate_shortcut.activated.connect(self.rotate_90)

        self.mini_screen = QExtendedToolButton()
        self.mini_screen.setIcon(QPixmap(f"{self._parent.theme_path}\\mini-screen.png"))
        self.mini_screen.clicked.connect(self.show_mini_screen)
        self.mini_screen_shortcut = QShortcut(QKeySequence(Qt.Key.Key_I), self._parent)
        self.mini_screen_shortcut.activated.connect(self.show_mini_screen)

        self.copy = QExtendedToolButton()
        self.copy.setIcon(QPixmap(f"{self._parent.theme_path}\\copy.png"))
        self.copy.clicked.connect(self.copy_img)

        self.open = QExtendedToolButton()
        self.open.setIcon(QPixmap(f"{self._parent.theme_path}\\open.png"))
        self.open.clicked.connect(self.open_file)

        self.info = QExtendedToolButton()
        self.info.setIcon(QPixmap(f"{self._parent.theme_path}\\info.png"))
        self.info.clicked.connect(self.show_info)

        self.addButton(self.back)
        self.addButton(self.next)
        self.addSeparator()
        self.addButton(self.zoom_in)
        self.addButton(self.zoom_out)
        self.addButton(self.rotate)
        self.addSeparator()
        self.addButton(self.mini_screen)
        self.addSeparator()
        self.addButton(self.copy)
        self.addButton(self.open)
        self.addButton(self.info)

        self.setIconSize(20, 20)
        self.setButtonsSize(30, 30)
        self.setSpacing(3)
        self.setOutline(5)
        self.adaptiveShowedWidth()
        self.adaptiveHidedWidth()

    def back_image(self):
        if self._current_index not in (-1, 0):
            self._transforms[self._images[self._current_index]] = self._view.transforms()

            self._current_index -= 1

            self._view.setPixmap(QPixmap(self._images[self._current_index]))
            self._parent.setWindowTitle(f"UPix - {os.path.split(self._images[self._current_index])[1]}")
            self._info_menu.setFileProperty(
                self._images[self._current_index],
                self._view.scene.pixmap().size().toTuple()
            )

            if self._images[self._current_index] in self._transforms:
                self._view.setTransforms(self._transforms[self._images[self._current_index]])
        else:
            self.moveDisabledButton(0)

    def next_image(self):
        if self._current_index not in (-1, len(self._images) - 1):
            self._transforms[self._images[self._current_index]] = self._view.transforms()

            self._current_index += 1

            self._view.setPixmap(QPixmap(self._images[self._current_index]))
            self._parent.setWindowTitle(f"UPix - {os.path.split(self._images[self._current_index])[1]}")
            self._info_menu.setFileProperty(
                self._images[self._current_index],
                self._view.scene.pixmap().size().toTuple()
            )

            if self._images[self._current_index] in self._transforms:
                self._view.setTransforms(self._transforms[self._images[self._current_index]])
        else:
            self.moveDisabledButton(1)

    def zoom_in_func(self):
        if self._current_index != -1:
            self._view.zoom(1)
        else:
            self.moveDisabledButton(3)

    def zoom_out_func(self):
        if self._current_index != -1:
            self._view.zoom(-1)
        else:
            self.moveDisabledButton(4)

    def rotate_90(self):
        if self._current_index != -1:
            self._view.rotate90()
        else:
            self.moveDisabledButton(5)

    def rotate_menu(self):
        if self._current_index != -1:
            self._info_menu.hideMenu()
            self._rotate_menu.showMenu()
        else:
            self.moveDisabledButton(5)

    def show_mini_screen(self):
        if self._current_index != -1:
            self._mini_screen = QMiniScreen(self._parent, self._view.scene.pixmap())
            self._mini_screen.show()
        else:
            self.moveDisabledButton(7)

    def copy_img(self):
        if self._current_index != -1:
            self._app.clipboard().setPixmap(self._view.scene.pixmap())
        else:
            self.moveDisabledButton(-3)

    def open_file(self):
        if path := QFileDialog.getOpenFileName(self, "Open Image",
                                               filter="Images (*.bmp *.cur *.gif *.icns *.jpeg *.jpg "
                                                      "*.pbm *.pdf *.pgm *.png *.ppm *.svg *.svgz "
                                                      "*.tga *.tif *.tiff *.wbmp *.webp *.xbm *.xpm)")[0]:
            self.load_image(path)

    def show_info(self):
        if self._current_index != -1:
            self._rotate_menu.hideMenu()

            self._info_menu.setFileProperty(
                self._images[self._current_index],
                self._view.scene.pixmap().size().toTuple()
            )
            self._info_menu.showMenu()
        else:
            self.moveDisabledButton(-1)

    def load_image(self, path: str):
        supported_formats = [chunk.toStdString() for chunk in QImageReader.supportedImageFormats()]
        parent_dir = os.path.split(path)[0]

        if path.split(".")[-1].lower() in supported_formats:
            self._images.clear()
            self._transforms.clear()
            for file in os.listdir(parent_dir):
                if file.split(".")[-1].lower() in supported_formats:
                    self._images.append(f"{parent_dir}\\{file}".replace("/", "\\"))

            self._current_index = self._images.index(path.replace("/", "\\"))

            self._view.setPixmap(QPixmap(path))
            self._parent.setWindowTitle(f"UPix - {os.path.split(path)[1]}")
            self._info_menu.setFileProperty(
                self._images[self._current_index],
                self._view.scene.pixmap().size().toTuple()
            )

            self._parent.showNormal()
