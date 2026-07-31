from django.db import models
from clubs.models import Club
from common.validators import Is30MinutesIncrement
from courts.models import Court


# Create your models here.
class ExceptionalUnavailability(models.Model):
    club = models.ForeignKey(
        to=Club, on_delete=models.CASCADE, related_name="unavailability"
    )
    court = models.ForeignKey(
        to=Court,
        on_delete=models.CASCADE,
        blank=True,
        related_name="exceptional_unavailability",
    )
    start_datetime = models.DateTimeField(validators=[Is30MinutesIncrement()])
    end_datetime = models.DateTimeField(validators=[Is30MinutesIncrement()])
