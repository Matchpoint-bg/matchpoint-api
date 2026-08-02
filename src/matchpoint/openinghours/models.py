from django.db import models
from clubs.models import Club
from common.validators import Is30MinutesIncrement


class OpeningHours(models.Model):
    class Meta:
        unique_together = ["club", "weekday"]

    class WeekdayChoices(models.TextChoices):
        MONDAY = "Monday", "Mon"
        TUESDAY = "Tuesday", "Tue"
        WEDNESDAY = "Wednesday", "Wed"
        THURSDAY = "Thursday", "Thu"
        FRIDAY = "Friday", "Fry"
        SATURDAY = "Saturday", "Sat"
        SUNDAY = "Sunday", "Sun"

    club = models.ForeignKey(
        to=Club, on_delete=models.CASCADE, related_name="opening_hour"
    )
    weekday = models.CharField(choices=WeekdayChoices.choices)
    opening_hour = models.TimeField(validators=[Is30MinutesIncrement()])
    closing_hour = models.TimeField(validators=[Is30MinutesIncrement()])
