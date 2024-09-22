# Nagad Payment Package README

This README provides an overview of the Nagad Payment Package, its components, and usage examples. The package is designed to facilitate payment processing with the Nagad payment gateway using Python and FastAPI.

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Usage](#usage)
    - [Initiating a Payment](#initiating-a-payment)
    - [Handling Payment Callbacks](#handling-payment-callbacks)
    - [Verifying a Payment](#verifying-a-payment)
5. [Error Handling](#error-handling)
6. [Contributing](#contributing)
7. [License](#license)

## 1. Introduction

The Nagad Payment Package allows you to easily integrate Nagad's payment gateway into your Python applications. It provides functionality for initiating payments, handling payment callbacks, and verifying payments. This package is designed to work with the Nagad payment gateway API.

## 2. Installation

You can install the Nagad Payment Package using pip:

```bash
pip install nagadpy
```

## 3. Configuration

Before using the package, you need to configure it with your Nagad merchant information. You'll need the following information:

- `MERCHANT_ID`: Your Nagad merchant ID.
- `BASE_URL`: The base URL of the Nagad payment gateway API.
- `CALLBACK_URL`: The URL where Nagad will send payment callbacks.
- `PUBLIC_KEY`: Your Nagad public key.
- `PRIVATE_KEY`: Your Nagad private key.

You can set these values as environment variables or hardcode them in your application. Make sure to keep your private key secure.

## 4. Usage

### Initiating a Payment

To initiate a payment, you can create an instance of the `NagadPayment` class and call the `checkout_process` method. Here's an example using FastAPI:

```python
from typing import Any
from fastapi import FastAPI
from nagadpy import NagadPayment

app = FastAPI()


@app.get("/")
def initiate_payment() -> Any:
    # Initialize NagadPayment with your merchant information
    nagad_payment = NagadPayment(
        merchant_id="YOUR_MERCHANT_ID",
        callback_url="YOUR_CALLBACK_URL",
        base_url="NAGAD_API_BASE_URL",
        public_key="YOUR_PUBLIC_KEY",
        private_key="YOUR_PRIVATE_KEY",
        client_ip_address="CLIENT_IP_ADDRESS",
    )

    try:
        payment_response = nagad_payment.checkout_process(
            amount="50.00",
            invoice_number="INVOICE_NUMBER",
        )
        # Handle the payment response, which contains the payment URL and status.
        # you can redirect url or you can send url to frontend based on status
        print(payment_response)
        #  {'callBackUrl': 'https://sandbox-ssl.mynagad.com:10061/check-out/MDkyMjIzMD', 'status': 'Success'}
    except Exception as e:
        # Handle any exceptions that may occur during the payment process
        logger.error(str(e))
    return {"payment_url": payment_response.get("callBackUrl"), "message": "success"}
```

### Handling Payment Callbacks

Nagad will send payment callbacks to the `CALLBACK_URL` you provided when initiating the payment. You can create an endpoint in your FastAPI application to handle these callbacks. Here's an example:

```python
from fastapi import FastAPI, Request
from nagadpy import NagadPaymentVerify

app = FastAPI()

@app.get("/payment-response")
@app.get("/payment-response", response_class=RedirectResponse, status_code=302):
    payment_response = dict(request.query_params)
    # or you can use payment_verify.parse_payment_response(query_string=params).
    # in that case you need to pass query string as str

    # handle payment_response
    order_id = payment_response.get("order_id")
    if payment_response.get("status") != "Success":
        print("Payment failed or cancel.Do the change your db")
        return f"http://127.0.0.1:8000/payment-status/?status=failed&user_tnx_ref={order_id}"

    # Verify the payment using the payment reference ID received in the callback
    payment_verify = NagadPaymentVerify(base_url="NAGAD_API_BASE_URL")
    payment_reference_id = payment_response.get("payment_ref_id")
    verification_result = payment_verify.verify_payment(payment_reference_id)

    # Handle the payment verification result
    if (
        verification_result.get("statusCode") == "000"
        and verification_result.get("status") == "Success"
        and verification_result.get("issuerPaymentRefNo")
    ):
        print("Do your business logic")
        return f"http://127.0.0.1:8000/payment-status/?status=success&user_tnx_ref={order_id}"
    else:
        print("Payment failed or cancel.Do the change your db")
        return f"http://127.0.0.1:8000/payment-status/?status=failed&user_tnx_ref={order_id}"
```

### Verifying a Payment

To verify a payment, you can use the `verify_payment` method of the `NagadPaymentVerify` class. This method sends a GET request to the Nagad payment verification endpoint. Here's an example:

```python
from nagadpy import NagadPaymentVerify

# Initialize NagadPaymentVerify with the Nagad API base URL
payment_verify = NagadPaymentVerify(base_url="NAGAD_API_BASE_URL")

# Specify the payment reference ID to verify
payment_reference_id = "YOUR_PAYMENT_REFERENCE_ID"

# Verify the payment
verification_result = payment_verify.verify_payment(payment_reference_id)

# Handle the payment verification result
print(verification_result)
```

## 5. Error Handling

The Nagad Payment Package provides custom exceptions for different stages of the payment process. You can catch and handle these exceptions to manage errors gracefully. The available exceptions include:

- `PaymentInitiationError`: Raised when an error occurs during payment initiation.
- `PaymentCompleteError`: Raised when an error occurs during payment completion.
- `PaymentVerificationError`: Raised when an error occurs during payment verification.
- `DecryptionError`: Raised when an error occurs during data decryption.
- `EncryptionError`: Raised when an error occurs during data encryption.
- `RequestError`: Raised when there is an issue with the HTTP request.
- `SignatureGenerationError`: Raised when an error occurs during signature generation.
- `CheckProcessError`: Raised when an error occurs during checkout process.

Make sure to handle these exceptions appropriately in your application.

## 6. Contributing

If you'd like to contribute to the Nagad Payment Package, please follow the standard open-source contribution guidelines, including creating issues, submitting pull requests, and adhering to the project's coding standards.

## 7. License

The Nagad Payment Package is provided under the [MIT License](LICENSE). You are free to use, modify, and distribute it according to the terms of the license.

---

This README provides a basic overview of the Nagad Payment Package. For more detailed information and examples, refer to the package's documentation and source code.
