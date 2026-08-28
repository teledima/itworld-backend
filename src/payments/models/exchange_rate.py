from django.db import models


class ExchangeRate(models.Model):
    base_currency = models.CharField(max_length=3)
    target_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=8, decimal_places=3)
    updated_at = models.DateTimeField(auto_now=True)
