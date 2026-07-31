from django.db import models
from common.validators import Is30MinutesIncrement
from courts.models import Court
from users.models import CustomUser


class Reservation(models.Model):
    court = models.ForeignKey(to=Court, on_delete=models.CASCADE)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField(validators=[Is30MinutesIncrement()])
    end_datetime = models.DateTimeField(validators=[Is30MinutesIncrement()])
    reservation_amt = models.FloatField(blank=True, null=True)
