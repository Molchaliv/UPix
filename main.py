import darkdetect
import json
import os
import sys

from qflat.application import QCustomizeWindow

from core.widgets import QGraphicsImageView

from core.fullscreen_menu import QFullScreenMenu
from core.info_menu import QInfoMenu
from core.mini_menu import QMiniMenu
from core.rotate_menu import QRotateMenu

from PySide6.QtCore import QSize
from PySide6.QtGui import QIcon, QResizeEvent
from PySide6.QtWidgets import QApplication


class QMainWindow(QCustomizeWindow):
    try:
        settings = json.load(open(f"{os.path.split(__file__)[0]}\\settings.json"))
    except json.JSONDecodeError:
        settings = {"theme": "system"}
    except FileNotFoundError:
        settings = {"theme": "system"}

    theme = darkdetect.theme().lower() if settings["theme"] == "system" else settings["theme"]
    theme_path = f"{os.path.split(__file__)[0]}\\ui\\icons\\{theme}-theme"

    def __init__(self):
        super(QMainWindow, self).__init__(use_mica="if available", theme="dark")

        self.view = QGraphicsImageView(self)

        self.full_screen = QFullScreenMenu(self)
        self.info_menu = QInfoMenu(self)
        self.rotate_menu = QRotateMenu(self, self.view)

        self.mini_menu = QMiniMenu(self, app, self.view, self.info_menu, self.rotate_menu)

        self.change_theme()
        self.setWindowIcon(QIcon(f"{os.path.split(__file__)[0]}\\ui\\icons\\icon.png"))
        self.setWindowTitle("UPix")
        self.setMinimumSize(QSize(450, 350))
        self.resize(QSize(800, 600))

    def change_theme(self):
        with open(f"{os.path.split(__file__)[0]}\\ui\\styles\\{self.theme}-theme.css", encoding="utf-8") as file:
            app.setStyleSheet(file.read())

    def resizeEvent(self, event: QResizeEvent):
        try:
            self.view.resize(self.width(), self.height() - 32)
            self.view.move(0, 32)

            self.full_screen.move(self.full_screen.getPos())
            self.info_menu.move(self.info_menu.getPos())
            self.mini_menu.move(self.mini_menu.getPos())

            self.rotate_menu.move(self.rotate_menu.getPos())
        except AttributeError:
            ...

        super(QMainWindow, self).resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main = QMainWindow()
    main.show()

    sys.exit(app.exec())
