import io
import os
from PIL import Image
from django.core.files.base import ContentFile


def convert_to_webp(image_field):
    img = Image.open(image_field)
    img = img.convert("RGB")
    img.thumbnail((1600, 1600))
    buffer = io.BytesIO()
    img.save(buffer, format="webp", quality=85, method=6)

    base = os.path.basename(image_field.name)

    filename = os.path.splitext(base)[0] + ".webp"

    return filename, ContentFile(buffer.getvalue())
