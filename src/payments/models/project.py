import uuid

from django.db import models

from payments.models import Merchant


class Project(models.Model):
    name = models.CharField()
    api_key = models.UUIDField(unique=True, default=uuid.uuid4)
    webhook_url = models.CharField()
    webhook_secret = models.CharField()
    merchant = models.ForeignKey(Merchant, on_delete=models.RESTRICT)

    created_at = models.DateTimeField(auto_now_add=True)

