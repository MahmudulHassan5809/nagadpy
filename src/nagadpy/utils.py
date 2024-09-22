import datetime
import random
import socket
import string

import pytz


def generate_challenge(string_length: int) -> str:
    """
    Generate a random challenge string consisting of lowercase letters.

    Args:
        string_length (int): The length of the generated challenge string.

    Returns:
        str: A random challenge string of the specified length.
    """
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(string_length))


def get_timestamp() -> str:
    """
    Get the current timestamp in the "YYYYMMDDHHMMSS" format for the Asia/Dhaka timezone.

    Returns:
        str: A timestamp string in the "YYYYMMDDHHMMSS" format.
    """
    tz = pytz.timezone("Asia/Dhaka")
    now = datetime.datetime.now(tz)
    return now.strftime("%Y%m%d%H%M%S")
