import os
import time


def resize(size: int | float, from_: str = "KB", to_: str = "B"):
    sizes = ("PB", "TB", "GB", "MB", "KB", "B")
    unit = sizes.index(to_.upper()) - sizes.index(from_.upper())

    return size / (1024 ** abs(unit)) if unit < 0 else size * (1024 ** abs(unit))


def maxsize(size: int | float):
    for unit in ("PB", "TB", "GB", "MB", "KB", "B"):
        if int(resize(size, "B", unit)) > 0:
            return f"{resize(size, 'B', unit):.2f} {unit}"


def image_aspect_ratio(width: int, height: int):
    for division in range(max(width, height), 1, -1):
        if not width % division and not height % division:
            return width // division, height // division

    return width, height


def get_info(path: str, size: tuple):
    return {
        "filename": os.path.split(path)[1],
        "size": maxsize(os.path.getsize(path)),
        "directory": os.path.split(path)[0],
        "datetime": time.ctime(os.path.getctime(path)),
        "image_size": f"{'×'.join(map(str, size))} "
                      f"({':'.join(map(str, image_aspect_ratio(*size)))})"
    }
