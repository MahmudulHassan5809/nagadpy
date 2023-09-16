import datetime
import random
import string

import pytz


def generate_challenge(string_length: int) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(string_length))


def get_timestamp():
    tz = pytz.timezone("Asia/Dhaka")
    now = datetime.datetime.now(tz)
    return now.strftime("%Y%m%d%H%M%S")
