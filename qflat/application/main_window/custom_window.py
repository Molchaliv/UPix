import winreg

import win32api
import win32con
import win32gui

from sys import getwindowsversion

from win32comext.shell import shellcon
from ctypes import Structure, c_int, POINTER, windll, byref, sizeof, cast
from ctypes.wintypes import DWORD, HWND, UINT, RECT, LPARAM, MSG, LPRECT

from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QGuiApplication, QPainter, QIcon, QPixmap, QCursor
from PySide6.QtWidgets import QWidget, QToolButton, QLabel, QHBoxLayout

from .window_effects import WindowsEffects
from .windows_resources import get_icons


class APPBARDATA(Structure):
    _fields_ = [
        ('cbSize',           DWORD),
        ('hWnd',             HWND),
        ('uCallbackMessage', UINT),
        ('uEdge',            UINT),
        ('rc',               RECT),
        ('lParam',           LPARAM)
    ]


class PWINDOWPOS(Structure):
    _fields_ = [
        ('hWnd',            HWND),
        ('hwndInsertAfter', HWND),
        ('x',               c_int),
        ('y',               c_int),
        ('cx',              c_int),
        ('cy',              c_int),
        ('flags',           UINT)
    ]


class NCCALCSIZE_PARAMS(Structure):
    _fields_ = [
        ('rgrc',  RECT*3),
        ('lppos', POINTER(PWINDOWPOS))
    ]


LPNCCALCSIZE_PARAMS = POINTER(NCCALCSIZE_PARAMS)


def is_maximized(h_wnd):
    win_placement = win32gui.GetWindowPlacement(h_wnd)
    if win_placement:
        return win_placement[1] == win32con.SW_MAXIMIZE
    return False


def get_monitor_info(h_wnd, dw_flags):
    monitor = win32api.MonitorFromWindow(h_wnd, dw_flags)
    if monitor:
        return win32api.GetMonitorInfo(monitor)


def is_full_screen(h_wnd):
    if not h_wnd:
        return False
    h_wnd = int(h_wnd)

    win_rect = win32gui.GetWindowRect(h_wnd)
    if not win_rect:
        return False

    monitor_info = get_monitor_info(h_wnd, win32con.MONITOR_DEFAULTTOPRIMARY)
    if not monitor_info:
        return False

    monitor_rect = monitor_info['Monitor']
    return all(i == j for i, j in zip(win_rect, monitor_rect))


def find_window(h_wnd):
    if not h_wnd:
        return

    windows = QGuiApplication.topLevelWindows()
    if not windows:
        return

    for window in windows:
        if window and int(window.winId()) == int(h_wnd):
            return window


def get_resize_border_thickness(h_wnd):
    window = find_window(h_wnd)
    if not window:
        return 0

    result = win32api.GetSystemMetrics(
        win32con.SM_CXSIZEFRAME) + win32api.GetSystemMetrics(92)

    if result > 0:
        return result

    b_result = c_int(0)

    windll.dwmapi.DwmIsCompositionEnabled(byref(b_result))
    thickness = 8 if bool(b_result.value) else 4
    return round(thickness * window.devicePixelRatio())


class Taskbar:
    LEFT = 0
    TOP = 1
    RIGHT = 2
    BOTTOM = 3
    NO_POSITION = 4

    AUTO_HIDE_THICKNESS = 2

    @staticmethod
    def is_auto_hide():
        appbar_data = APPBARDATA(
            sizeof(APPBARDATA), 0, 0, 0, RECT(0, 0, 0, 0), 0)
        taskbar_state = windll.shell32.SHAppBarMessage(
            shellcon.ABM_GETSTATE, byref(appbar_data))
        return taskbar_state == shellcon.ABS_AUTOHIDE

    @classmethod
    def get_position(cls, h_wnd):
        monitor_info = get_monitor_info(
            h_wnd, win32con.MONITOR_DEFAULTTONEAREST)
        if not monitor_info:
            return cls.NO_POSITION

        monitor = RECT(*monitor_info['Monitor'])
        appbar_data = APPBARDATA(sizeof(APPBARDATA), 0, 0, 0, monitor, 0)
        for position in (cls.LEFT, cls.TOP, cls.RIGHT, cls.BOTTOM):
            appbar_data.uEdge = position
            if windll.shell32.SHAppBarMessage(11, byref(appbar_data)):
                return position

        return cls.NO_POSITION


def invert_color(color):
    inverted_color = ''
    for i in range(0, 5, 2):
        channel = int(color[i:i + 2], base=16)
        inverted_color += hex(round(channel / 6))[2:].upper().zfill(2)
    inverted_color += color[-2:]
    return inverted_color


def is_system_dark_mode():
    path = r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize"
    name = r"AppsUseLightTheme"
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, path) as registry_key:
        value, regtype = winreg.QueryValueEx(registry_key, name)
    return not bool(value)


class CustomBase(QWidget):
    def __init__(self, use_mica='false', theme='auto', color="F0F0F0A0"):
        """ Customizable window without titlebar

        Parameters
        ----------
        use_mica: 'false', 'true', 'if available'
            Use mica or acrylic effect,
            'if available' mode will select according to the current OS
        theme: 'auto', 'dark', 'light'
            Use dark, light or system theme
        color: str
            Window background color
        """
        super().__init__()
        self.is_win11 = getwindowsversion().build >= 22000
        if use_mica == 'true' and not self.is_win11:
            raise ValueError("Wrong argument 'use_mica': "
                             "mica available only in Windows 11")
        if use_mica == 'if available':
            self.use_mica = self.is_win11
        elif use_mica == 'true':
            self.use_mica = True
        elif use_mica == 'false':
            self.use_mica = False
        else:
            raise ValueError("Wrong argument 'use_mica': "
                             "can be 'false', 'true' or 'if available'")
        if theme == 'auto':
            self.dark_mode = is_system_dark_mode()
        elif theme == 'dark':
            self.dark_mode = True
        elif theme == 'light':
            self.dark_mode = False
        else:
            raise ValueError("Wrong argument 'theme': "
                             "can be 'auto', 'dark' or 'light'")
        if self.use_mica and not color:
            raise ValueError("Wrong argument 'color': can't be used with mica")
        elif len(color) != 8 and not self.use_mica:
            raise ValueError("Wrong argument 'color': must be 8 len")
        if self.dark_mode:
            self.acrylic_color = invert_color(color)
        else:
            self.acrylic_color = color
        self.effect_enabled = False
        self.__effect_timer = None

        self.win_effects = WindowsEffects()
        self.win_effects.add_window_animation(self.winId())
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.win_effects.add_window_animation(self.winId())
        self.set_effect()
        if self.is_win11:
            self.win_effects.add_blur_behind_window(self.winId())
            self.win_effects.add_shadow_effect(self.winId())
        self.setStyleSheet("CustomBase{ background: #202020; }")

        self.__effect_timer = QTimer(self)
        self.__effect_timer.setInterval(100)
        self.__effect_timer.setSingleShot(True)
        self.__effect_timer.timeout.connect(self.set_effect)

    def set_effect(self, enable=True):
        if self.effect_enabled == enable:
            return
        self.effect_enabled = enable
        if enable and self.use_mica:
            self.win_effects.add_mica_effect(self.winId(), self.dark_mode)
        elif enable:
            self.win_effects.add_acrylic_effect(
                self.winId(), self.acrylic_color)
        else:
            self.win_effects.remove_background_effect(self.winId())
        self.update()

    def _temporary_disable_effect(self):
        self.set_effect(False)
        self.__effect_timer.stop()
        self.__effect_timer.start()

    def moveEvent(self, event):
        if self.is_win11 or not self.__effect_timer:
            return super().moveEvent(event)
        self._temporary_disable_effect()

    def paintEvent(self, event):
        if self.effect_enabled:
            return super().paintEvent(event)
        painter = QPainter(self)
        painter.setOpacity(0.8)
        if self.dark_mode:
            painter.setBrush(Qt.GlobalColor.black)
        else:
            painter.setBrush(Qt.GlobalColor.white)
        painter.drawRect(self.rect())

    def nativeEvent(self, event_type, message):
        msg = MSG.from_address(int(message))
        if not msg.hWnd:
            return False, 0
        if msg.message == win32con.WM_NCCALCSIZE:
            if msg.wParam:
                rect = cast(msg.lParam, LPNCCALCSIZE_PARAMS).contents.rgrc[0]
            else:
                rect = cast(msg.lParam, LPRECT).contents

            is_max = is_maximized(msg.hWnd)
            is_full = is_full_screen(msg.hWnd)

            # Adjust the size of client rect
            if is_max and not is_full:
                thickness = get_resize_border_thickness(msg.hWnd)
                rect.top += thickness
                rect.left += thickness
                rect.right -= thickness
                rect.bottom -= thickness

            # Handle the situation that an auto-hide taskbar is enabled
            if (is_max or is_full) and Taskbar.is_auto_hide():
                position = Taskbar.get_position(msg.hWnd)
                if position == Taskbar.LEFT:
                    rect.top += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.BOTTOM:
                    rect.bottom -= Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.LEFT:
                    rect.left += Taskbar.AUTO_HIDE_THICKNESS
                elif position == Taskbar.RIGHT:
                    rect.right -= Taskbar.AUTO_HIDE_THICKNESS

            res = 0 if not msg.wParam else win32con.WVR_REDRAW
            return True, res

        return False, 0


class TitleBarButton(QToolButton):
    def __init__(self, parent, dark_mode):
        super().__init__(parent)

        self.dark_mode = dark_mode

        if dark_mode:
            colors = "FFFFFF"
            self._icon_color = Qt.GlobalColor.white
        else:
            colors = "000000"
            self._icon_color = Qt.GlobalColor.black
        self.setFixedSize(46, 32)
        style = """
        TitleBarButton{
            background-color: transparent;
            border: none;
            border-radius: 0px;
            margin: 0px;
        }
        TitleBarButton:hover{
            background-color: #20""" + colors + """;
        }
        TitleBarButton:pressed{
            background-color: #40""" + colors + """;
        }
        """
        self.setStyleSheet(style)


class MinimizeButton(TitleBarButton):
    def __init__(self, parent, dark_mode):
        super().__init__(parent, dark_mode)

        pixmap = QPixmap()
        pixmap.loadFromData(get_icons(self.dark_mode)["minimize"])

        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(11, 11))


class MaximizeButton(TitleBarButton):
    def __init__(self, parent, dark_mode):
        super().__init__(parent, dark_mode)

        self.is_max = False

        pixmap = QPixmap()
        pixmap.loadFromData(get_icons(self.dark_mode)["maximize"])

        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(10, 10))

    def restate(self):
        self.is_max = not self.is_max

        pixmap = QPixmap()
        pixmap.loadFromData(get_icons(self.dark_mode)["restore" if self.is_max else "maximize"])

        self.setIcon(QIcon(pixmap))
        self.setIconSize(QSize(10, 10))

class CloseButton(TitleBarButton):
    def __init__(self, parent, dark_mode):
        super().__init__(parent, dark_mode)

        style = self.styleSheet()[:self.styleSheet().find('}') + 1]
        style += """
        TitleBarButton:hover{
            background-color: #C42B1C;
        }
        TitleBarButton:pressed{
            background-color: #C83C30;
        }"""

        self._light_pixmap = QPixmap()
        self._light_pixmap.loadFromData(get_icons(True)["close"])

        self._dark_pixmap = QPixmap()
        self._dark_pixmap.loadFromData(get_icons(False)["close"])

        self.setIcon(QIcon(self._light_pixmap if self.dark_mode else self._dark_pixmap))
        self.setIconSize(QSize(10, 10))
        self.setStyleSheet(style)

    def enterEvent(self, event):
        if self.dark_mode:
            return

        self.setIcon(QIcon(self._light_pixmap))

    def leaveEvent(self, event):
        if self.dark_mode:
            return

        self.setIcon(QIcon(self._dark_pixmap))


class TitleBar(QWidget):
    def __init__(self, parent, dark_mode):
        super().__init__(parent)
        self.setFixedHeight(32)

        self.icon = QLabel(self)
        self.title = QLabel(self)
        self.min_btn = MinimizeButton(self, dark_mode)
        self.max_btn = MaximizeButton(self, dark_mode)
        self.close_btn = CloseButton(self, dark_mode)
        self.h_box_layout = QHBoxLayout(self)

        if dark_mode:
            self.title.setStyleSheet("color: white")
        # self.icon.setFixedSize(10, 16)
        self.h_box_layout.setSpacing(0)
        self.h_box_layout.setContentsMargins(0, 0, 0, 0)

        self.h_box_layout.addWidget(self.icon)
        self.h_box_layout.addWidget(self.title)
        self.h_box_layout.addWidget(self.min_btn)
        self.h_box_layout.addWidget(self.max_btn)
        self.h_box_layout.addWidget(self.close_btn)

        self.min_btn.clicked.connect(self.window().showMinimized)
        self.max_btn.clicked.connect(self.__toggle_max_state)
        self.close_btn.clicked.connect(self.window().close)

    def __toggle_max_state(self):
        is_max = self.window().isMaximized()
        self.max_btn.restate()
        if is_max:
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.__toggle_max_state()

    def mouseMoveEvent(self, event):
        if not event.pos().x() < self.width() - 46 * 3:
            return
        win32gui.ReleaseCapture()
        win32api.SendMessage(
            int(self.window().winId()),
            win32con.WM_SYSCOMMAND, win32con.SC_MOVE | win32con.HTCAPTION, 0
        )


class CustomWindow(CustomBase):
    BORDER_WIDTH = 4

    def __init__(self, use_mica='false', theme='auto', color="20202099"):
        """ Customizable window with custom titlebar

        Parameters
        ----------
        use_mica: 'false', 'true', 'if available'
            Use mica or acrylic effect,
            'if available' mode will select according to the current OS
        theme: 'auto', 'dark', 'light'
            Use dark, light or system theme
        color: str
            Window background color
        """
        self.title_bar = None
        super().__init__(use_mica, theme, color)
        self.title_bar = TitleBar(self, self.dark_mode)

    def setWindowTitle(self, title):
        # self.title_bar.title.setText(title)
        super().setWindowTitle(title)

    def setWindowIcon(self, icon):
        self.title_bar.icon.setFixedSize(QSize(32, 32))
        self.title_bar.icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_bar.icon.setPixmap(icon.pixmap(16, 16))
        super().setWindowIcon(icon)

    def resizeEvent(self, event):
        if not self.title_bar:  # if not initialized
            return
        self.title_bar.setFixedWidth(self.width())
        if not self.use_mica:
            self._temporary_disable_effect()

    def nativeEvent(self, event_type, message):
        msg = MSG.from_address(int(message))
        if not msg.hWnd:
            return False, 0
        if msg.message == win32con.WM_NCHITTEST:
            pos = QCursor.pos()
            x = pos.x() - self.x()
            y = pos.y() - self.y()
            lx = x < self.BORDER_WIDTH
            rx = x > self.width() - self.BORDER_WIDTH
            ty = y < self.BORDER_WIDTH
            by = y > self.height() - self.BORDER_WIDTH
            if rx and by:
                return True, win32con.HTBOTTOMRIGHT
            elif rx and ty:
                return True, win32con.HTTOPRIGHT
            elif lx and by:
                return True, win32con.HTBOTTOMLEFT
            elif lx and ty:
                return True, win32con.HTTOPLEFT
            elif rx:
                return True, win32con.HTRIGHT
            elif by:
                return True, win32con.HTBOTTOM
            elif lx:
                return True, win32con.HTLEFT
            elif ty:
                return True, win32con.HTTOP

        return super().nativeEvent(event_type, message)
