import hmac
import secrets
import hashlib


def generate_signature(secret, payload):
    signature = hmac.new(key=secret.encode(), msg=payload.encode(), digestmod=hashlib.sha256).hexdigest()
    return f"sha256={signature}"


def generate_secret_key():
    return secrets.token_urlsafe(32)
