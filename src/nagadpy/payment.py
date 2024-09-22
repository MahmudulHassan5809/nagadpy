import base64
import json
from dataclasses import dataclass

import requests
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from nagadpy.exceptions import (
    CheckProcessError,
    DecryptionError,
    EncryptionError,
    PaymentCompleteError,
    PaymentInitiationError,
    RequestError,
    SignatureGenerationError,
)
from nagadpy.utils import generate_challenge, get_timestamp


@dataclass
class NagadPayment:
    base_url: str
    merchant_id: str
    callback_url: str
    private_key: str
    public_key: str
    client_ip_address: str

    @property
    def is_ready(self) -> bool:
        """Check if all required properties are set."""
        return all(
            getattr(self, attr, None) is not None for attr in self.__annotations__
        )

    def _generate_signature(self, data: str) -> str:
        """
        Generate a digital signature for the given data using the private key.

        Args:
            data (str): The data to be signed.

        Returns:
            Tuple[str, Optional[Exception]]: A tuple containing the generated signature as a
            base64-encoded string and an optional exception if an error occurs during the
            signature generation. If the operation is successful, the second element will be None.
        """

        try:
            pk = (
                "-----BEGIN RSA PRIVATE KEY-----\n"
                + self.private_key
                + "\n-----END RSA PRIVATE KEY-----"
            )
            private_key = serialization.load_pem_private_key(
                pk.encode(), password=None, backend=default_backend()
            )
            sign = private_key.sign(data.encode(), padding.PKCS1v15(), hashes.SHA256())
            signature = base64.b64encode(sign)
            return signature.decode("utf-8")
        except Exception as e:
            raise SignatureGenerationError(
                f"Error generating signature: {str(e)}"
            ) from e

    def _encrypt_data_using_public_key(self, data: str) -> str:
        """
        Encrypt sensitive data using the provided public key.

        Args:
            data (str): The sensitive data to be encrypted.

        Returns:
            Tuple[str, Optional[Exception]]: A tuple containing the encrypted data as a
            base64-encoded string and an optional exception if an error occurs during the
            encryption. If the operation is successful, the second element will be None.
        """
        try:
            pk = (
                "-----BEGIN PUBLIC KEY-----\n"
                + self.public_key
                + "\n-----END PUBLIC KEY-----"
            )
            public_key = serialization.load_pem_public_key(
                pk.encode(), backend=default_backend()
            )
            encrypted_data = public_key.encrypt(data.encode(), padding.PKCS1v15())
            encoded_data = base64.b64encode(encrypted_data)
            return encoded_data.decode("utf-8")
        except Exception as e:
            raise EncryptionError(f"Error encrypting data: {str(e)}") from e

    def _decrypt_data_using_private_key(self, data: bytes) -> str:
        """
        Decrypts the provided encrypted data using the merchant's private key.

        Args:
            data (str): The encrypted data to be decrypted.

        Returns:
            str: The decrypted plaintext message.

        Raises:
            DecryptionError: If an error occurs during the decryption process.

        Note:
            This method assumes that the private key has been previously loaded and is stored
            in the `private_key` attribute of the class.

        Example:
            To decrypt encrypted_data using a merchant's private key, you can call this method as follows:

            decrypted_message = self._decrypt_data_using_private_key(encrypted_data)
        """

        merchant_private_key = self.private_key

        try:
            pk = (
                "-----BEGIN RSA PRIVATE KEY-----\n"
                + merchant_private_key
                + "\n-----END RSA PRIVATE KEY-----"
            )
            private_key = serialization.load_pem_private_key(
                pk.encode(), password=None, backend=default_backend()
            )
            original_message = private_key.decrypt(data, padding.PKCS1v15())
            return original_message.decode("utf-8")
        except Exception as e:
            raise DecryptionError(f"Error decrypting data: {str(e)}") from e

    def _send_request(self, data: dict, url: str) -> dict:
        """
        Sends an HTTP POST request to the specified URL with the provided JSON data and headers.

        Args:
            data (dict): A dictionary representing the JSON data to be sent in the request body.
            url (str): The URL to which the request will be sent.

        Returns:
            dict: A dictionary representing the JSON response from the server.

        Raises:
            RequestError: If there is an error during the request or if the response status code is not 200.

        Note:
            This method sends a POST request with JSON data and includes specific headers such as "Content-Type",
            "X-KM-IP-V4", "X-KM-Client-Type", and "X-KM-Api-Version".

        Example:
            To send a request with JSON data to a specific URL, you can call this method as follows:

            request_data = {"key1": "value1", "key2": "value2"}
            response_data = self._send_request(request_data, "https://example.com/api")
        """

        headers = {
            "Content-Type": "application/json",
            "X-KM-IP-V4": self.client_ip_address,
            "X-KM-Client-Type": "PC_WEB",
            "X-KM-Api-Version": "v-0.2.0",
        }

        try:
            response = requests.post(url, json.dumps(data), headers=headers)
            json_response = response.json()
            if response.status_code != 200:
                raise RequestError(
                    f"HTTP error {response.status_code}: {json_response}"
                )
            return json_response
        except Exception as e:
            raise RequestError(f"Request error: {str(e)}")

    def _initiate_payment(self, invoice_number: str) -> dict:
        """
        Initiates a payment by sending a request to the payment gateway's initialization endpoint.

        Args:
            invoice_number (str): The unique invoice number or identifier for the payment.

        Returns:
            dict: A dictionary containing the response from the payment gateway.

        Raises:
            PaymentInitiationError: If there is an error during payment initiation, including issues with
                signature generation, data encryption, or the HTTP request.

        Example:
            To initiate a payment, you can call this method with the invoice number:

            payment_info = self._initiate_payment("INV12345")
        """

        try:
            now = get_timestamp()
            sensitive_data = {
                "merchantId": self.merchant_id,
                "orderId": invoice_number,
                "challenge": generate_challenge(40),
                "datetime": now,
            }
            sensitive_data_str = json.dumps(sensitive_data)
            encrypted_sensitive_data = self._encrypt_data_using_public_key(
                sensitive_data_str
            )
            signature = self._generate_signature(sensitive_data_str)
            data = {
                "dateTime": now,
                "sensitiveData": encrypted_sensitive_data,
                "signature": signature,
            }
            url = f"{self.base_url}/check-out/initialize/{self.merchant_id}/{invoice_number}"
            result = self._send_request(data=data, url=url)
            return result
        except (SignatureGenerationError, EncryptionError, RequestError) as e:
            raise PaymentInitiationError(str(e)) from e
        except Exception as e:
            raise PaymentInitiationError(str(e))

    def _complete_payment(
        self,
        amount: str,
        invoice_number: str,
        challenge: str,
        payment_reference_id: str,
    ) -> dict:
        """
        Completes a payment by sending a request to the payment gateway's completion endpoint.

        Args:
            amount (str): The amount to be paid.
            invoice_number (str): The unique invoice number or identifier for the payment.
            challenge (str): A challenge associated with the payment.
            payment_reference_id (str): The reference identifier for the payment.

        Returns:
            dict: A dictionary containing the response from the payment gateway.

        Raises:
            PaymentCompleteError: If there is an error during payment completion, including issues with
                signature generation, data encryption, or the HTTP request.

        Example:
            To complete a payment, you can call this method with the required parameters:

            payment_info = self._complete_payment("100.00", "INV12345", "challenge123", "REF456")
        """

        try:
            sensitive_data = {
                "merchantId": self.merchant_id,
                "orderId": invoice_number,
                "currencyCode": "050",
                "amount": amount,
                "challenge": challenge,
            }

            sensitive_data_str = json.dumps(sensitive_data)
            encrypt_result = self._encrypt_data_using_public_key(sensitive_data_str)

            signature_result = self._generate_signature(sensitive_data_str)

            data = {
                "dateTime": get_timestamp(),
                "sensitiveData": encrypt_result,
                "signature": signature_result,
                "merchantCallbackURL": self.callback_url,
                "additionalMerchantInfo": {},
            }

            url = f"{self.base_url}/check-out/complete/{payment_reference_id}"

            result = self._send_request(data=data, url=url)
            return result
        except (SignatureGenerationError, EncryptionError, RequestError) as e:
            raise PaymentCompleteError(str(e)) from e
        except Exception as e:
            raise PaymentCompleteError(str(e))

    def checkout_process(self, amount: str, invoice_number: str) -> dict:
        """
        Initiates and completes the payment process for a given amount and invoice number.

        Args:
            amount (str): The amount to be paid.
            invoice_number (str): The unique invoice number or identifier for the payment.

        Returns:
            dict: A dictionary containing the response from the payment gateway after completion.
            Example:  ```{"callBackUrl": "", "status": ""}```

        Raises:
            PaymentCompleteError: If there is an error during the payment process, including issues with
                initiation, decryption, completion, or missing required data.


        Example:
            To perform a payment process, you can call this method with the amount and invoice number:
            ```
            nagad_payment = NagadPayment(
                merchant_id=MERCHANT_ID,
                callback_url=CALLBACK_URL,
                base_url=BASE_URL,
                public_key=PUBLIC_KEY,
                private_key=PRIVATE_KEY,
            )
            payment_response = nagad_payment.checkout_process("100.00", "INV12345")
            ```

        Callback Response:
            Method: GET
            QueryParams Example:
            ```
            {
                "merchant": "",
                "order_id": "",
                "payment_ref_id": "",
                "status": "",
                "status_code": "",
                "message": ""
            }
            ```
        """
        if not self.is_ready:
            raise ValueError("All payment information properties must be set")
        try:
            initiated_result = self._initiate_payment(invoice_number=invoice_number)

            sensitive_data = initiated_result.get("sensitiveData")

            if not sensitive_data:
                raise CheckProcessError(
                    "sensitive data is missing from initiated_result"
                )

            decrypted_result = self._decrypt_data_using_private_key(
                base64.b64decode(sensitive_data)
            )

            decrypted_sensitive_data_dict = json.loads(decrypted_result)

            if not decrypted_sensitive_data_dict.get(
                "paymentReferenceId"
            ) or not decrypted_sensitive_data_dict.get("challenge"):
                raise CheckProcessError(
                    "paymentReferenceId and challenge data is missing from initiated_result"
                )

            payment_reference_id = decrypted_sensitive_data_dict.get(
                "paymentReferenceId"
            )
            challenge = decrypted_sensitive_data_dict.get("challenge")
            complete_result = self._complete_payment(
                amount=amount,
                invoice_number=invoice_number,
                challenge=challenge,
                payment_reference_id=payment_reference_id,
            )
            return complete_result
        except (DecryptionError, PaymentInitiationError, PaymentCompleteError) as e:
            raise PaymentCompleteError(str(e)) from e
        except Exception as e:
            raise PaymentCompleteError(str(e))
