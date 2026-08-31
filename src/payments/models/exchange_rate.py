from django.db import models


class ExchangeRate(models.Model):
    base_currency = models.CharField(max_length=3)
    target_currency = models.CharField(max_length=3)
    rate = models.DecimalField(max_digits=18, decimal_places=10)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['base_currency', 'target_currency'],
                include=['rate'],
                name='exchangerate_base_target_currency_key'
            )
        ]