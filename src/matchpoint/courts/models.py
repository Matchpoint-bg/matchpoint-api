from django.db import models


class Court(models.Model):
    class CourtType(models.TextChoices):
        GRASS = ("Grass", "Grass")
        CLAY = ("Clay", "Clay")
        HARD = ("Hard", "Hard")

    class SportType(models.TextChoices):
        TENNIS = ("Tennis", "Tennis")

    club_id = models.ForeignKey(
        to="clubs.Club", on_delete=models.CASCADE, related_name="courts"
    )
    name = models.CharField(max_length=50)
    sport_type = models.CharField(choices=SportType.choices)
    surface_type = models.CharField(choices=CourtType.choices)
    is_indoor = models.BooleanField()
    is_lit = models.BooleanField()


class CourtImages(models.Model):
    court_id = models.ForeignKey(
        to=Court, on_delete=models.CASCADE, related_name="images"
    )
    image = models.ImageField(upload_to="courts")
