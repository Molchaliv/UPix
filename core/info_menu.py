import pyperclip

from .utils import get_info
from .widgets import QExtendedToolButton, QExtendedMenu

from PySide6.QtCore import QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QLineEdit


class QWidgetStub(QWidget):
    theme_path: str = ""


class QInfoLabel(QLineEdit):
    def __init__(self, *args, **kwargs):
        super(QInfoLabel, self).__init__(*args, **kwargs)

        self.setReadOnly(True)


class QInfoToolButton(QExtendedToolButton):
    def __init__(self, *args, **kwargs):
        super(QInfoToolButton, self).__init__(*args, **kwargs)


class QInfoMenu(QExtendedMenu):
    def __init__(self, parent: QWidget | QWidgetStub):
        super(QInfoMenu, self).__init__(parent=parent)

        self.close_button = QExtendedToolButton(self)
        self.close_button.setIcon(QPixmap(f"{parent.theme_path}\\close.png"))
        self.close_button.resize(QSize(30, 30))
        self.close_button.setIconSize(QSize(20, 20))
        self.close_button.move(260, 10)
        self.close_button.clicked.connect(self.hideMenu)

        self.filename = QLabel("Filename:", self)
        self.filename.move(10, 50)
        self.datetime = QLabel("Datetime:", self)
        self.datetime.move(10, 90)
        self.file_size = QLabel("File size:", self)
        self.file_size.move(10, 130)
        self.image_resolution = QLabel("Image resolution:", self)
        self.image_resolution.move(10, 170)
        self.file_path = QLabel("File path:", self)
        self.file_path.move(10, 210)

        self.filename_info = QInfoLabel("", self)
        self.filename_info.resize(150, self.filename_info.height())
        self.filename_info.move(140, 50)

        self.datetime_info = QInfoLabel("", self)
        self.datetime_info.resize(150, self.datetime_info.height())
        self.datetime_info.move(140, 90)

        self.file_size_info = QInfoLabel("", self)
        self.file_size_info.resize(150, self.file_size_info.height())
        self.file_size_info.move(140, 130)

        self.image_resolution_info = QInfoLabel("", self)
        self.image_resolution_info.resize(150, self.image_resolution_info.height())
        self.image_resolution_info.move(140, 170)

        self.file_path_info = QInfoLabel("", self)
        self.file_path_info.resize(110, self.file_path_info.height())
        self.file_path_info.move(140, 210)

        self.file_path_copy = QInfoToolButton(self)
        self.file_path_copy.setIcon(QPixmap(f"{parent.theme_path}\\copy.png"))
        self.file_path_copy.resize(QSize(30, 30))
        self.file_path_copy.setIconSize(QSize(17, 17))
        self.file_path_copy.move(260, 210)
        self.file_path_copy.clicked.connect(lambda: pyperclip.copy(self.file_path_info.text()))

        self.setDuration(650)
        self.resize(300, 250)
        self.move(self.getPos())

    def setFileProperty(self, path: str, size: tuple):
        data = get_info(path, size)
        _size_info = "×".join(map(str, size))

        self.filename_info.setText(data["filename"])
        self.filename_info.setToolTip(data["filename"])
        self.filename_info.setCursorPosition(0)
        self.datetime_info.setText(data["datetime"])
        self.datetime_info.setToolTip(data["datetime"])
        self.datetime_info.setCursorPosition(0)
        self.file_size_info.setText(data["size"])
        self.file_size_info.setToolTip(data["size"])
        self.file_size_info.setCursorPosition(0)
        self.image_resolution_info.setText(data["image_size"])
        self.image_resolution_info.setToolTip(data["image_size"])
        self.image_resolution_info.setCursorPosition(0)
        self.file_path_info.setText(path)
        self.file_path_info.setToolTip(path)
        self.file_path_info.setCursorPosition(0)
