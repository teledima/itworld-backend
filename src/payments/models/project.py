from django.db import models
from payments.models.merchant import Merchant


class Project(models.Model):
    name = models.CharField()
    api_key = models.CharField(unique=True)
    webhook_url = models.CharField()
    webhook_secret = models.CharField()
    merchant = models.ForeignKey(Merchant, on_delete=models.RESTRICT)

    created_at = models.DateTimeField(auto_now_add=True)

