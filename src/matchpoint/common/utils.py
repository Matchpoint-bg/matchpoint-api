import io
import os
from PIL import Image
import cloudinary
from django.core.files.base import ContentFile
from django.apps import apps


def convert_to_webp(image_field, club_id: int, app_label, model_name):
    model = apps.get_model(app_label, model_name)
    club = model.objects.get(pk=club_id)
    img = Image.open(image_field)

    img.thumbnail((1600, 1600))

    if img.mode != "RGB":
        img = img.convert("RGB")

    buffer = io.BytesIO()

    img.save(buffer, format="webp", quality=85, method=6)

    buffer.seek(0)

    result = cloudinary.uploader.upload(
        buffer, folders="club", public_id=f"club_{club_id}_header", format="webp"
    )

    club.header_image = result["public_id"]
    club.pending_header_image.delete(save=False)

    club.save(update_fields=["header_image"])

    return result["public_id"], ContentFile(buffer.getvalue())
