from django.db import models


class ExchangeRate(models.Model):
    base_currency = models.CharField(max_length=3)
    target_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=18, decimal_places=10)
    updated_at = models.DateTimeField(auto_now=True)
