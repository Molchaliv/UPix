import os

from PIL import Image, ImageDraw


def invert(image: Image.Image) -> Image.Image:
    drawer = ImageDraw.Draw(image)
    pixels = image.load()
    for x in range(image.size[0]):
        for y in range(image.size[1]):
            data = pixels[x, y]
            if data != (0, 0, 0, 0) and isinstance(data, tuple):
                drawer.point((x, y), (255 - data[0], 255 - data[1], 255 - data[2], data[3]))

    return image


for file in os.listdir("./ui/icons"):
    if not os.path.isdir(f"./ui/icons/{file}"):
        original = Image.open(f"./ui/icons/{file}")
        if original.format != "RGBA":
            original = original.convert("RGBA")
            original.save(f"./ui/icons/{file}")

        invert(original.copy()).save(f"./ui/icons/dark-theme/{file}")
