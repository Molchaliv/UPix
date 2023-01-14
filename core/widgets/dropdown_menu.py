from PySide6.QtCore import QPoint, QSize, QTimer, QThread, QEvent, QPropertyAnimation, \
    QParallelAnimationGroup, QEasingCurve, Signal
from PySide6.QtGui import QEnterEvent, QMouseEvent
from PySide6.QtWidgets import QWidget, QFrame, QAbstractButton


class QBorderRadiusAnimation(QTimer):
    def __init__(self, *args, **kwargs):
        super(QBorderRadiusAnimation, self).__init__(*args, **kwargs)

        self._start_value: int = 0
        self._end_value: int = 0
        self._current_value: int = 0
        self._step: int = 1

        self._thread: QThread = QThread()

        self.timeout.connect(self._updateBorderRadius)
        self.moveToThread(self._thread)

    def _updateBorderRadius(self):
        self._current_value += self._step
        if self._current_value == self._end_value:
            self.stop()

        self.parent().setStyleSheet(
            f"{self.parent().__class__.__name__} {{ border-radius: {self._current_value}px; }}"
        )

    def setStartValue(self, value: int):
        self._start_value = value

    def setEndValue(self, value: int):
        self._end_value = value

    def setDuration(self, msecs: int):
        self.setInterval((msecs // abs(self._end_value - self._start_value)) - 50)

        if self._end_value > self._start_value:
            self._current_value, self._step = self._start_value, 1
        else:
            self._current_value, self._step = self._start_value, -1

    def start(self):
        super(QBorderRadiusAnimation, self).start()

        self._thread.start()


class QSeparator(QFrame):
    def __init__(self, parent: QWidget = None):
        super(QSeparator, self).__init__(parent=parent)

        self.setMaximumWidth(1)
        self.setMinimumWidth(1)
        self.setFixedWidth(1)


class QDropdownMenu(QFrame):
    showed = Signal(bool)
    hided = Signal(bool)

    def __init__(self, parent: QWidget = None):
        super(QDropdownMenu, self).__init__(parent=parent)

        self._parent: QWidget = parent
        self._buttons: list[QAbstractButton | QSeparator] = []
        self._current_state: str = "hide"
        self._showed_width: int = 200
        self._hided_width: int = 60
        self._pinned: bool = False
        self._spacing: int = 10
        self._outline: int = 10
        self._last_pos: int = 10
        self._base_size: tuple[int, int] = (30, 30)
        self._icon_size: tuple[int, int] = (20, 20)
        self._animation_0: QPropertyAnimation | QParallelAnimationGroup | None = None
        self._animation_1: QPropertyAnimation | QParallelAnimationGroup | None = None
        self._animation: QPropertyAnimation | QParallelAnimationGroup | None = None

    def setPinState(self, state: bool):
        self._pinned = state

    def setMenuState(self, state: str):
        self._current_state = state

        self.updateMenuState()

    def updateMenuState(self):
        if self._current_state == "hide":
            self.resize(self._hided_width, 10)
            self.move((self.parent().width() // 2) - (self._hided_width // 2), 10)
            self.setStyleSheet("border-radius: 4px;")
        else:
            self.resize(self._showed_width, 10)
            self.move((self.parent().width() // 2) - (self._showed_width // 2), 10)
            self.setStyleSheet("border-radius: 10px;")

    def renderButtons(self):
        pos_x = self._outline
        for button in self._buttons:
            if isinstance(button, QAbstractButton):
                button.resize(QSize(*self._base_size))
                button.setIconSize(QSize(*self._icon_size))
                button.move(pos_x, 10)
            else:
                button.resize(1, self._base_size[1] - 6)
                button.move(pos_x, 13)

            pos_x += button.width() + self._spacing
        self._last_pos = pos_x

        self.updateMenuState()

    def getPos(self):
        return QPoint((self.parent().width() // 2) - (self.width() // 2), 10)

    def adaptiveShowedWidth(self):
        self._showed_width = self._last_pos - self._spacing + self._outline

        self.updateMenuState()

    def adaptiveHidedWidth(self):
        self._hided_width = (self._showed_width * 10) // (self._base_size[1] + self._outline + 10)

        self.updateMenuState()

    def setShowedWidth(self, width: int):
        self._showed_width = width

    def setHidedWidth(self, width: int):
        self._hided_width = width

    def setOutline(self, outline: int):
        self._outline = outline

        self.renderButtons()

    def setSpacing(self, spacing: int):
        self._spacing = spacing

        self.renderButtons()

    def setButtonsSize(self, width: int, height: int):
        self._base_size = (width, height)

        self.renderButtons()
        self.resize(self.width(), height + self._outline + 10)

    def setIconSize(self, width: int, height: int):
        self._icon_size = (width, height)

        self.renderButtons()
        self.resize(self.width(), height + self._outline + 10)

    def moveDisabledButton(self, index: int):
        if self._current_state == "show" and not self._animation_0:
            self._animation_0 = QPropertyAnimation(self._buttons[index], b"pos")
            self._animation_0.setStartValue(QPoint(self._buttons[index].x() + 2, 10))
            self._animation_0.setEndValue(QPoint(self._buttons[index].x() - 2, 10))
            self._animation_0.setDuration(100)

            self._animation_1 = QPropertyAnimation(self._buttons[index], b"pos")
            self._animation_1.setStartValue(QPoint(self._buttons[index].x() - 2, 10))
            self._animation_1.setEndValue(QPoint(self._buttons[index].x(), 10))
            self._animation_1.setDuration(100)

            self._animation_1.finished.connect(self.deleteAnimations)
            self._animation_0.finished.connect(self._animation_1.start)
            self._animation_0.start()

    def addButton(self, button: QAbstractButton):
        button.setParent(self)
        button.resize(QSize(*self._base_size))
        button.setIconSize(QSize(*self._icon_size))
        button.move(self._last_pos, 10)

        self._last_pos += button.width() + self._spacing
        self._buttons.append(button)

        return len(self._buttons) - 1

    def addSeparator(self):
        separator = QSeparator(self)
        separator.resize(1, self._base_size[1] - 6)
        separator.move(self._last_pos, 13)

        self._last_pos += separator.width() + self._spacing
        self._buttons.append(separator)

        return len(self._buttons) - 1

    def showMenu(self):
        self._current_state = "show"

        if not self._pinned:
            animation_move = QPropertyAnimation(self, b"pos")
            animation_move.setStartValue(self.pos())
            animation_move.setEndValue(QPoint((self.parent().width() // 2) - (self._showed_width // 2), 10))
            animation_move.setDuration(450)
            animation_move.setEasingCurve(QEasingCurve.Type.OutExpo)

            animation_size = QPropertyAnimation(self, b"size")
            animation_size.setStartValue(self.size())
            animation_size.setEndValue(QSize(self._showed_width, self._base_size[1] + self._outline + 10))
            animation_size.setDuration(450)
            animation_size.setEasingCurve(QEasingCurve.Type.OutExpo)

            animation_radius = QBorderRadiusAnimation(self)
            animation_radius.setStartValue(4)
            animation_radius.setEndValue(10)
            animation_radius.setDuration(450)
            animation_radius.start()

            for widget in self._buttons:
                widget.show()

            self._animation = QParallelAnimationGroup(self)
            self._animation.addAnimation(animation_move)
            self._animation.addAnimation(animation_size)
            self._animation.start()

            return True
        return False

    def hideMenu(self):
        self._current_state = "hide"

        if not self._pinned:
            animation_move = QPropertyAnimation(self, b"pos")
            animation_move.setStartValue(self.pos())
            animation_move.setEndValue(QPoint((self.parent().width() // 2) - (self._hided_width // 2), 10))
            animation_move.setDuration(450)
            animation_move.setEasingCurve(QEasingCurve.Type.OutExpo)

            animation_size = QPropertyAnimation(self, b"size")
            animation_size.setStartValue(self.size())
            animation_size.setEndValue(QSize(self._hided_width, 10))
            animation_size.setDuration(450)
            animation_size.setEasingCurve(QEasingCurve.Type.OutExpo)

            animation_radius = QBorderRadiusAnimation(self)
            animation_radius.setStartValue(10)
            animation_radius.setEndValue(4)
            animation_radius.setDuration(450)
            animation_radius.start()

            for widget in self._buttons:
                widget.hide()

            self._animation = QParallelAnimationGroup(self)
            self._animation.addAnimation(animation_move)
            self._animation.addAnimation(animation_size)
            self._animation.start()

            return True
        return False

    def deleteAnimations(self):
        self._animation_0 = None
        self._animation_1 = None

    def enterEvent(self, event: QEnterEvent):
        self.showed.emit(self.showMenu())

    def leaveEvent(self, event: QEvent):
        self.hided.emit(self.hideMenu())

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        self._pinned = not self._pinned
