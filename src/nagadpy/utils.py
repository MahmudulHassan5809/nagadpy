import datetime
import random
import string
import base64
import pytz
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.backends import default_backend
from .settings import (
    NAGAD_PUBLIC_KEY,
    NAGAD_PRIVATE_KEY,
)


def generate_challenge(string_length: int) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for _ in range(string_length))


def get_timestamp():
    tz = pytz.timezone("Asia/Dhaka")
    now = datetime.datetime.now(tz)
    return now.strftime("%Y%m%d%H%M%S")


def encrypt_data_using_public_key(data):
    pg_public_key = NAGAD_PUBLIC_KEY
    pk = "-----BEGIN PUBLIC KEY-----\n" + pg_public_key + "\n-----END PUBLIC KEY-----"
    try:
        public_key = serialization.load_pem_public_key(
            pk.encode(), backend=default_backend()
        )
        encrypted_data = public_key.encrypt(data.encode(), padding.PKCS1v15())
        print("private key encrypted data = ", encrypted_data)
        data = base64.b64encode(encrypted_data)
        return data.decode("utf-8"), None
    except Exception as e:
        print("ERROR encrypt_data_using_public_key : ", e)
        return None, e


def generate_signature(data: str):
    merchant_private_key = NAGAD_PRIVATE_KEY
    pk = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        + merchant_private_key
        + "\n-----END RSA PRIVATE KEY-----"
    )
    try:
        private_key = serialization.load_pem_private_key(
            pk.encode(), password=None, backend=default_backend()
        )
        sign = private_key.sign(data.encode(), padding.PKCS1v15(), hashes.SHA256())
        signature = base64.b64encode(sign)
        return signature.decode("utf-8"), None
    except Exception as e:
        print("ERROR generate_signature : ", e)
        return None, e


def decrypt_data_using_private_key(data: str):
    merchant_private_key = NAGAD_PRIVATE_KEY
    pk = (
        "-----BEGIN RSA PRIVATE KEY-----\n"
        + merchant_private_key
        + "\n-----END RSA PRIVATE KEY-----"
    )
    try:
        private_key = serialization.load_pem_private_key(
            pk.encode(), password=None, backend=default_backend()
        )
        original_message = private_key.decrypt(data, padding.PKCS1v15())
        return original_message.decode("utf-8"), None
    except Exception as e:
        print("ERROR decrypt_data_using_private_key : ", e)
        return None, e
