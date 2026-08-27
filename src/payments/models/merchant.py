from django.db import models


class Merchant(models.Model):
    MerchantStatus = models.TextChoices("StatusEnum", "ACTIVE BLOCKED")

    name = models.CharField()
    status = models.CharField(choices=MerchantStatus)

    created_at = models.DateTimeField(auto_now_add=True)
