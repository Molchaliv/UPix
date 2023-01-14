from PySide6.QtCore import QPoint, QPropertyAnimation, QEasingCurve
from PySide6.QtWidgets import QFrame


class QExtendedMenu(QFrame):
    def __init__(self, *args, **kwargs):
        super(QExtendedMenu, self).__init__(*args, **kwargs)

        self._animation: QPropertyAnimation | None = None
        self._is_hided: bool = True
        self._duration: int = 500

        self.move(self.getPos())

    def getPos(self):
        if not self._is_hided:
            return QPoint(
                (self.parent().width() // 2) - (self.width() // 2),
                self.parent().height() - (self.height() + 10)
            )

        return QPoint((self.parent().width() // 2) - (self.width() // 2), self.parent().height())

    def setDuration(self, duration: int):
        self._duration = duration

    def updateMenu(self, pos: QPoint):
        self._animation = QPropertyAnimation(self, b"pos")
        self._animation.setStartValue(self.pos())
        self._animation.setEndValue(pos)
        self._animation.setDuration(self._duration)
        self._animation.setEasingCurve(QEasingCurve.Type.OutExpo)
        self._animation.start()

    def showMenu(self):
        self._is_hided = False

        self.updateMenu(self.getPos())

    def hideMenu(self):
        self._is_hided = True

        self.updateMenu(self.getPos())
