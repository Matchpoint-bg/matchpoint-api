from django.db import models
from courts.models import Court
from users.models import CustomUser


class Reservation(models.Model):
    court = models.ForeignKey(to=Court, on_delete=models.CASCADE)
    user = models.ForeignKey(to=CustomUser, on_delete=models.CASCADE)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    reservation_amt = models.FloatField(blank=True, null=True)
