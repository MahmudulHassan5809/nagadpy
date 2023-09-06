import datetime
import random
import string


def generate_challenge(string_length: int) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(string_length))


def get_timestamp() -> str:
    utc_offset = datetime.timedelta(hours=6)
    now = datetime.datetime.now() + utc_offset
    return now.strftime("%Y%m%d%H%M%S")
