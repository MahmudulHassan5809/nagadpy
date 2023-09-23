from dataclasses import dataclass

import requests
from nagadpy.exceptions import PaymentVerificationError


@dataclass
class NagadPaymentVerify:
    base_url: str

    def parse_payment_response(self, query_string: str) -> dict[str, str]:
        """
        Parse a query string and return a dictionary of key-value pairs.

        Args:
            query_string (str): The input query string.

        Returns:
            dict[str, str]: A dictionary containing the parsed key-value pairs.
        """
        query_params = query_string.split("&")
        params_dict = {}

        for param in query_params:
            key, value = param.split("=")
            params_dict[key] = value

        return params_dict

    def verify_payment(self, payment_reference_id: str) -> dict:
        """
        Verifies a payment using the provided payment reference ID by sending a GET request to
        the payment verification endpoint.

        Args:
            payment_reference_id (str): The reference identifier for the payment to be verified.

        Returns:
            dict: A dictionary containing the response from the payment verification endpoint.

        Raises:
            PaymentVerificationError: If there is an error during payment verification or if the
                verification request fails.

        Example:
            To verify a payment using its reference ID, you can call this method as follows:
            ```
            payment_verify = NagadPaymentVerify(base_url=BASE_URL)
            verification_result = payment_verify.verify_payment("REF456789")
            ```
        """
        try:
            url = f"{self.base_url}/verify/payment/{payment_reference_id}"
            response = requests.get(url)
            return response.json()
        except Exception as e:
            raise PaymentVerificationError(str(e))
