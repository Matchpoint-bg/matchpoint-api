from django.db import models
from common.tasks import convert_image_task
from cloudinary.models import CloudinaryField
from django.core.files.uploadedfile import InMemoryUploadedFile
from cloudinary import CloudinaryResource
from common.validators import CustomImageFormatValidator


class Club(models.Model):
    class CityChoices(models.TextChoices):
        SOFIA = ("Sofia", "SOF")

    name = models.CharField(max_length=100, unique=True, null=False, blank=False)
    city = models.CharField(choices=CityChoices.choices, default=CityChoices.SOFIA)
    address = models.CharField(max_length=300, null=True, blank=True)
    post_code = models.CharField(max_length=8)
    latitude = models.FloatField()
    longitude = models.FloatField()
    description = models.CharField(max_length=1000, null=True, blank=True)
    website = models.URLField(null=True, blank=True)
    phone = models.CharField(max_length=12)
    email = models.EmailField()
    employees = models.ManyToManyField(to="users.CustomUser", related_name="club")
    header_image = CloudinaryField(null=True, validators=[CustomImageFormatValidator()])

    def save(self, *args, **kwargs):
        if self.header_image:
            if isinstance(self, CloudinaryResource):
                if self.header_image.format != "webp":
                    convert_image_task.delay(
                        self._meta.app_label,
                        self.__class__.__name__,
                        self.pk,
                        "image",
                    )
            elif isinstance(self, InMemoryUploadedFile):
                print("Trigger here")
                if not self.name.endswith(".webp"):
                    convert_image_task.delay(
                        self._meta.app_label,
                        self.__class__.__name__,
                        self.pk,
                        "image",
                    )

        return super().save(*args, **kwargs)
