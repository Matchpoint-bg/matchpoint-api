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
    header_image = models.ImageField(null=True)
