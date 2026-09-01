from django.db import models


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
    header_image = models.ImageField(null=True, upload_to="clubs/")

    # def save(self, *args, **kwargs):
    #
    #     should_convert = isinstance(
    #         self.header_image, InMemoryUploadedFile
    #     ) and not self.header_image.name.lower().endswith(".webp")
    #
    #     super().save(*args, **kwargs)
    #
    #     if should_convert:
    #         transaction.on_commit(
    #             lambda: convert_image_task.delay(
    #                 self._meta.app_label,
    #                 self.__class__.__name__,
    #                 self.pk,
    #                 "header_image",
    #             )
    #         )
