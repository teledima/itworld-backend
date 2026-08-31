import hashlib
import hmac
import json

import requests

from payments.models import Notification


def send(n: Notification):
    payload = {
        'invoice_id': n.invoice.pk,
        'status': n.invoice.status,
        'dt': n.invoice.updated_at.isoformat(),
        'type': 'invoice.closed',
    }

    signature = hmac.new(
        bytes(n.invoice.project.webhook_secret, encoding='utf-8'),
        bytes(json.dumps(payload), encoding='utf-8'),
        digestmod=hashlib.sha256,
    )

    requests.post(
        n.invoice.project.webhook_url,
        json=payload,
        headers={
            'X-Signature': signature.digest().hex(),
            'Idempotency-Key': n.idempotency_key,
        }
    )
