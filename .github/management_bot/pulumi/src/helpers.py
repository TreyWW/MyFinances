import base64


def encode_private_key(entire_key: str) -> str:
    return base64.b64encode(entire_key.encode("ascii")).decode("ascii")


def decode_private_key(raw_private_key) -> str:
    return base64.b64decode(raw_private_key.encode("ascii")).decode("ascii")
