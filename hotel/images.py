"""Make uploaded photos web-friendly.

Every photo uploaded through the admin panel is turned the right way up,
shrunk to at most 1920 px, stripped of its metadata (camera details, GPS
location) and saved as JPEG. A smaller copy is made for suite cards and
gallery thumbnails.
"""

from io import BytesIO
from pathlib import Path

from django.core.files.base import ContentFile
from PIL import Image, ImageCms, ImageOps

MAX_SIZE = 1920
THUMB_SIZE = (800, 1600)
QUALITY = 85
THUMB_QUALITY = 80


def _to_jpeg(img, quality):
    if img.mode != "RGB":
        img = img.convert("RGB")
    buffer = BytesIO()
    img.save(buffer, "JPEG", quality=quality, optimize=True, progressive=True)
    return ContentFile(buffer.getvalue())


def jpeg_name(name, suffix=""):
    return f"{Path(name).stem}{suffix}.jpg"


def prepare(data):
    """Return (main, thumbnail) for the uploaded bytes.

    `main` is None when the upload is already a small JPEG without metadata,
    so it is stored untouched instead of being compressed a second time.
    """
    original = Image.open(BytesIO(data))
    is_clean_jpeg = (
        original.format == "JPEG"
        and max(original.size) <= MAX_SIZE
        and not original.info.get("exif")
        and not original.info.get("icc_profile")
    )
    img = ImageOps.exif_transpose(original)
    icc = original.info.get("icc_profile")
    if icc:
        # Phones often save in a wide colour space; browsers expect sRGB.
        try:
            img = ImageCms.profileToProfile(
                img.convert("RGB"),
                ImageCms.ImageCmsProfile(BytesIO(icc)),
                ImageCms.createProfile("sRGB"),
                outputMode="RGB",
            )
        except (OSError, ImageCms.PyCMSError):
            pass
    main = None
    if not is_clean_jpeg:
        img.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)
        main = _to_jpeg(img, QUALITY)
    thumb = img.copy()
    thumb.thumbnail(THUMB_SIZE, Image.LANCZOS)
    return main, _to_jpeg(thumb, THUMB_QUALITY)
