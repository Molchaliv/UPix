import sys

from application import QCustomizeWindow

from PySide6.QtWidgets import QApplication


if __name__ == "__main__":
    app = QApplication(sys.argv)

    main = QCustomizeWindow(use_mica="true", theme="dark")
    main.show()

    sys.exit(app.exec())
