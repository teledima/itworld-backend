from django.db import models


class MerchantStatus(models.TextChoices):
    ACTIVE = 'ACTIVE'
    BLOCKED = 'BLOCKED'


class Merchant(models.Model):
    name = models.CharField()
    status = models.CharField(choices=MerchantStatus)

    created_at = models.DateTimeField(auto_now_add=True)
