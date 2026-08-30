from celery import shared_task
import cloudinary
from django.apps import apps
from common.utils import convert_to_webp


@shared_task
def convert_image_task(
    app_label: str, model_name: str, instance_id: int, image_field: str = "image"
):
    model = apps.get_model(app_label, model_name)
    instance = model.objects.get(pk=instance_id)
    image = getattr(instance, image_field)
    if image is not None and hasattr(image, "name"):
        original_file_name = image.name.lower()

        if not original_file_name.endswith(".webp"):
            file_name, content = convert_to_webp(
                image, instance.pk, app_label, model_name
            )
            result = cloudinary.uploader.upload(
                content,
                folder="club",
                public_id=f"club_{instance_id}_header",
                format="webp",
            )

            instance.header_image = result["public_id"]
            instance.pending_header_image.delete(save=False)

            instance.save(update_fields=["header_image"])
