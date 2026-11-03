"""
Сжимает фото для сайта: JPG/PNG/HEIC -> WebP, длинная сторона до 2000 px.

Установка (один раз):
    pip install pillow pillow-heif

Использование:
    python compress.py "ПАПКА_С_ИСХОДНИКАМИ" img
    python compress.py "G:/Мой диск/Фотограф/Свадьба 1" img --prefix story1

С --prefix файлы будут названы story1-1.webp, story1-2.webp ... (как в index.html).
Без --prefix имя берётся от исходного файла.
"""
import argparse
from pathlib import Path

from PIL import Image, ImageOps

try:
    import pillow_heif  # фото с iPhone (.heic)
    pillow_heif.register_heif_opener()
except ImportError:
    pass

EXT = {".jpg", ".jpeg", ".png", ".heic", ".webp", ".tif", ".tiff"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src", help="папка с исходниками")
    ap.add_argument("dst", nargs="?", default="img", help="куда сохранить (по умолчанию img)")
    ap.add_argument("--max", type=int, default=2000, help="длинная сторона, px")
    ap.add_argument("--q", type=int, default=80, help="качество WebP 1-100")
    ap.add_argument("--prefix", help="переименовать в PREFIX-1.webp, PREFIX-2.webp ...")
    a = ap.parse_args()

    src, dst = Path(a.src), Path(a.dst)
    dst.mkdir(parents=True, exist_ok=True)
    files = sorted(p for p in src.iterdir() if p.suffix.lower() in EXT)
    if not files:
        print("В папке нет фото:", src)
        return

    before = after = 0
    for i, p in enumerate(files, 1):
        im = ImageOps.exif_transpose(Image.open(p))  # правильный поворот
        im = im.convert("RGB")
        im.thumbnail((a.max, a.max), Image.LANCZOS)
        name = f"{a.prefix}-{i}.webp" if a.prefix else p.stem + ".webp"
        out = dst / name
        im.save(out, "WEBP", quality=a.q, method=6)
        before += p.stat().st_size
        after += out.stat().st_size
        print(f"{p.name}  ->  {name}  ({out.stat().st_size // 1024} КБ)")

    print(f"\nГотово: {len(files)} фото, {before / 1e6:.1f} МБ -> {after / 1e6:.1f} МБ")


if __name__ == "__main__":
    main()
