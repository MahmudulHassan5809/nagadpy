import base64
import json
from dataclasses import dataclass

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

from .utils import generate_challenge, get_timestamp


@dataclass
class NagadPayment:
    merchant_id: str
    base_url: str
    amount: str
    initiate_payment_path: str
    complete_payment_path: str
    callback_url: str
    invoice_number: str
    host_ip: str
    private_key: str
    public_key: str

    def _generate_signature(self, data: str) -> tuple[str, Exception | None]:
        """
        Generate a digital signature for the given data using the private key.

        Args:
            data (str): The data to be signed.

        Returns:
            Tuple[str, Optional[Exception]]: A tuple containing the generated signature as a
            base64-encoded string and an optional exception if an error occurs during the
            signature generation. If the operation is successful, the second element will be None.
        """
        pk = (
            "-----BEGIN RSA PRIVATE KEY-----\n"
            + self.private_key
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
            return None, e

    def _encrypt_data_using_public_key(self, data: str) -> tuple[str, Exception | None]:
        """
        Encrypt sensitive data using the provided public key.

        Args:
            data (str): The sensitive data to be encrypted.

        Returns:
            Tuple[str, Optional[Exception]]: A tuple containing the encrypted data as a
            base64-encoded string and an optional exception if an error occurs during the
            encryption. If the operation is successful, the second element will be None.
        """

        pk = (
            "-----BEGIN PUBLIC KEY-----\n"
            + self.public_key
            + "\n-----END PUBLIC KEY-----"
        )
        try:
            public_key = serialization.load_pem_public_key(
                pk.encode(), backend=default_backend()
            )
            encrypted_data = public_key.encrypt(data.encode(), padding.PKCS1v15())
            data = base64.b64encode(encrypted_data)
            return data.decode("utf-8"), None
        except Exception as e:
            return None, e

    def _decrypt_data_using_private_key(self, data: str) -> tuple:
        merchant_private_key = self.private_key
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
            return None, e

    def _send_request(self, data: dict, url: str) -> tuple:
        headers = {
            "Content-Type": "application/json",
            "X-KM-IP-V4": self.host_ip,
            "X-KM-Client-Type": "PC_WEB",
            "X-KM-Api-Version": "v-0.2.0",
        }

        try:
            response = requests.post(url, json.dumps(data), headers=headers)
            json_response = response.json()
            if response.status_code != 200:
                return None, json_response
            return json_response, None
        except Exception as e:
            return None, e

    def _initiate_payment(self):
        now = get_timestamp()

        sensitive_data = {
            "merchantId": self.merchant_id,
            "orderId": self.invoice_number,
            "challenge": generate_challenge(40),
            "datetime": now,
        }

        sensitive_data_str = json.dumps(sensitive_data.model_dump())

        encrypted_sensitive_data, err = self._encrypt_data_using_public_key(
            sensitive_data_str
        )

        if err:
            return None, err

        signature, err = self._generate_signature(sensitive_data_str)

        if err:
            return None, err

        data = {
            "dateTime": now,
            "sensitiveData": encrypted_sensitive_data,
            "signature": signature,
        }

        url = f"{self.base_url}/{self.initiate_payment_path}/{self.merchant_id}/{self.invoice_number}"

        result, error = self._send_request(data=data, url=url)

        return result, error

    def _complete_payment(
        self,
        challenge: str,
        payment_reference_id: str,
    ):
        sensitive_data = {
            "merchantId": self.merchant_id,
            "orderId": self.invoice_number,
            "currencyCode": "050",
            "amount": self.amount,
            "challenge": challenge,
        }

        sensitive_data_str = json.dumps(sensitive_data)
        encrypt_result, encrypt_err = self._encrypt_data_using_public_key(
            sensitive_data_str
        )

        if encrypt_err:
            return None, encrypt_err

        signature_result, signature_err = self._generate_signature(sensitive_data_str)

        if signature_err:
            return None, signature_err

        data = {
            "dateTime": get_timestamp(),
            "sensitiveData": encrypt_result,
            "signature": signature_result,
            "merchantCallbackURL": self.callback_url,
            "additionalMerchantInfo": {},
        }

        url = f"{self.base_url}/{self.complete_payment_path}/{payment_reference_id}"

        result, error = self._send_request(data=data, url=url)

        return result, error

    def nagad_checkout_process(self):
        initiated_result, initiated_err = self._initiate_payment()

        if initiated_err or not initiated_result.get("sensitiveData"):
            return None, initiated_err

        sensitive_data = initiated_result.get("sensitiveData")

        decrypted_result, decrypted_err = self._decrypt_data_using_private_key(
            base64.b64decode(sensitive_data)
        )

        if decrypted_err:
            return None, decrypted_err

        decrypted_sensitive_data_dict = json.loads(decrypted_result)

        if not decrypted_sensitive_data_dict.get(
            "paymentReferenceId"
        ) or not decrypted_sensitive_data_dict.get("challenge"):
            return None, decrypted_err

        payment_reference_id = decrypted_sensitive_data_dict.get("paymentReferenceId")
        challenge = decrypted_sensitive_data_dict.get("challenge")

        complete_result, complete_err = self._complete_payment(
            challenge, payment_reference_id
        )
        return complete_result, complete_err
