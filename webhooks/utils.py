import hashlib
from django.conf import settings

def verify_signature(payload, signature):
    raw = f"{payload['transaction_id']}{settings.WEBHOOK_SECRET}"
    expected = hashlib.sha256(raw.encode()).hexdigest()
    return expected == signature
