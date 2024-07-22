import base64
import random
import string


def encode_private_key(entire_key: str) -> str:
    return base64.b64encode(entire_key.encode("ascii")).decode("ascii")


def decode_private_key(raw_private_key) -> str:
    return base64.b64decode(raw_private_key.encode("ascii")).decode("ascii")


def del_reply_comment() -> str:
    return (
        "> If you would like to ignore this message, please reply with the reference `DELREPLY-"
        + "".join(random.choices(string.ascii_uppercase + string.digits, k=8))
        + "` (you may delete this reply afterwards)"
    )
