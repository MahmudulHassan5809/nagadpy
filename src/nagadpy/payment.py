import json
import base64
import requests
from .utils import (
    get_timestamp,
    generate_challenge,
    encrypt_data_using_public_key,
    generate_signature,
    decrypt_data_using_private_key,
)
from .settings import (
    NAGAD_BASE_URL,
    NAGAD_COMPLETE_PAYMENT_URL,
    NAGAD_INTIATE_PAYMENT_URL,
    NAGAD_MERCHANT_CALLBACK_URL,
    NAGAD_MERCHANT_ID,
)


def initiate_payment(invoice_number: str, host_ip: str):
    now = get_timestamp()
    sensitive_data = {
        "merchantId": NAGAD_MERCHANT_ID,
        "datetime": now,
        "orderId": invoice_number,
        "challenge": generate_challenge(40),
    }
    print("sensitive_data = ", sensitive_data)
    sensitive_data_str = json.dumps(sensitive_data)

    encrypted_sensitive_data, err = encrypt_data_using_public_key(sensitive_data_str)

    if err:
        return None, err

    signature, err = generate_signature(sensitive_data_str)

    if err:
        return None, err

    data = {
        "dateTime": now,
        "sensitiveData": encrypted_sensitive_data,
        "signature": signature,
    }
    headers = {
        "Content-Type": "application/json",
        "X-KM-IP-V4": host_ip,
        "X-KM-Client-Type": "PC_WEB",
        "X-KM-Api-Version": "v-0.2.0",
    }

    url = f"{NAGAD_BASE_URL}/{NAGAD_INTIATE_PAYMENT_URL}/{NAGAD_MERCHANT_ID}/{invoice_number}"
    try:
        print(url, json.dumps(data), "initiate_payment request url payload")
        response = requests.post(url, json.dumps(data), headers=headers)
        json_response = response.json()
        print("initiate_payment json_response = ", json_response, response.status_code)
        if response.status_code != 200:
            return None, json_response
        return json_response, None
    except Exception as e:
        print("ERROR initiate_payment", e)
        return None, e


def complete_payment(invoice_number, amount, challenge, payment_reference_id, host_ip):
    sensitive_data = {
        "merchantId": NAGAD_MERCHANT_ID,
        "orderId": invoice_number,
        "currencyCode": "050",
        "amount": amount,
        "challenge": challenge,
    }

    sensitive_data_str = json.dumps(sensitive_data)
    encrypt_sensitive_data, err = encrypt_data_using_public_key(sensitive_data_str)

    if err:
        return None, err
    signature, err = generate_signature(sensitive_data_str)

    if err:
        return None, err
    data = {
        "dateTime": get_timestamp(),
        "sensitiveData": encrypt_sensitive_data,
        "signature": signature,
        "merchantCallbackURL": NAGAD_MERCHANT_CALLBACK_URL,
        "additionalMerchantInfo": {},
    }
    host_ip = host_ip
    headers = {
        "Content-Type": "application/json",
        "X-KM-IP-V4": host_ip,
        "X-KM-Client-Type": "PC_WEB",
        "X-KM-Api-Version": "v-0.2.0",
    }

    url = f"{NAGAD_BASE_URL}/{NAGAD_COMPLETE_PAYMENT_URL}/{payment_reference_id}"
    try:
        print(url, json.dumps(data), "complete_payment request url payload")
        response = requests.post(url, data=json.dumps(data), headers=headers)
        json_response = response.json()
        print("complete_payment json_response = ", json_response, response.status_code)
        if response.status_code != 200:
            return None, json_response
        return json_response, None
    except Exception as e:
        print("ERROR complete_payment", e)
        return None, e


def nagad_checkout_process(invoice_number, amount, host_ip):
    host_ip = host_ip
    initiated_data, err = initiate_payment(invoice_number, host_ip)
    print("initiated_data = ", initiated_data)

    if err:
        return None, err

    sensitive_data = initiated_data.get("sensitiveData")
    if sensitive_data is None:
        return None, err

    decrypted_sensitive_data, err = decrypt_data_using_private_key(
        base64.b64decode(sensitive_data)
    )
    print("decrypted_sensitive_data = ", decrypted_sensitive_data)

    if err:
        return None, err

    decrypted_sensitive_data_dict = json.loads(decrypted_sensitive_data)

    payment_reference_id = decrypted_sensitive_data_dict.get("paymentReferenceId")
    challenge = decrypted_sensitive_data_dict.get("challenge")

    if payment_reference_id is None or challenge is None:
        return None, err

    result, err = complete_payment(
        invoice_number, amount, challenge, payment_reference_id, host_ip
    )
    print("complete_payment result lambda_handler: ", result)
    return result, err
