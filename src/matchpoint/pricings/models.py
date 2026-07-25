from django.db import models


class Prices(models.Model):
    class Meta:
        unique_together = [["court", "weekday", "time_start", "time_end"]]

    court = models.ForeignKey(to="courts.Court", on_delete=models.CASCADE)
    weekday = models.CharField()
    time_start = models.TimeField()
    time_end = models.TimeField()
    price_per_30_minutes = models.FloatField()
