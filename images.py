from PIL import Image
from pillow_heif import register_heif_opener

register_heif_opener()

wmax, hmax = max_size = (800, 800)

def compress_image(path: str) -> Image:
    img = Image.open(path)
    w,h = img.size

    if w > wmax or h > hmax:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

    return img.convert("RGB")

def save_image(img: Image, path: str) -> None:
    img.save(path)

