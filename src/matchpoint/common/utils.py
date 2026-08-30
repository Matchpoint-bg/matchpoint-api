import io
from PIL import Image
from django.core.files.base import ContentFile


def convert_to_webp(image):
    img = Image.open(image)

    img.thumbnail((1600, 1600))

    if img.mode != "RGB":
        img = img.convert("RGB")

    buffer = io.BytesIO()

    img.save(buffer, format="webp", quality=85, method=6)

    buffer.seek(0)

    return ContentFile(buffer.getvalue())
