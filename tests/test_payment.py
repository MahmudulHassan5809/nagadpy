from unittest.mock import MagicMock, patch

import pytest
from nagadpy.payment import NagadPayment


@pytest.fixture
def nagad_payment() -> NagadPayment:
    nagad_payment = NagadPayment(
        base_url="https://example.com",
        merchant_id="merchant_id",
        callback_url="https://callback.com",
        private_key="dummy_private_key",
        public_key="dummy_public_key",
    )
    return nagad_payment


def test_is_ready(nagad_payment: NagadPayment) -> None:
    assert nagad_payment.is_ready


@patch.object(NagadPayment, "_generate_signature", return_value="dummy_signature")
def test_generate_signature_method(
    mock_generate_signature: MagicMock, nagad_payment: NagadPayment
) -> None:
    data = "test_data"
    signature = nagad_payment._generate_signature(data)
    assert signature == "dummy_signature"


@patch.object(
    NagadPayment, "_encrypt_data_using_public_key", return_value="dummy_encrypted_data"
)
def test_encrypt_data_using_public_key(
    mock_encrypt_data: MagicMock, nagad_payment: NagadPayment
) -> None:
    data = "test_data"
    encrypted_data = nagad_payment._encrypt_data_using_public_key(data)
    assert encrypted_data == "dummy_encrypted_data"


@patch.object(
    NagadPayment, "_decrypt_data_using_private_key", return_value="dummy_decrypted_data"
)
def test_decrypt_data_using_private_key(
    mock_decrypt_data: MagicMock, nagad_payment: NagadPayment
) -> None:
    data = b"test_data"
    decrypted_data = nagad_payment._decrypt_data_using_private_key(data)
    assert decrypted_data == "dummy_decrypted_data"


@patch.object(NagadPayment, "_send_request", return_value={"status": "success"})
def test_send_request(
    mock_send_request: MagicMock, nagad_payment: NagadPayment
) -> None:
    data = {"key": "value"}
    url = "https://example.com/api"
    response = nagad_payment._send_request(data, url)
    assert response == {"status": "success"}


@patch.object(
    NagadPayment, "_encrypt_data_using_public_key", return_value="dummy_encrypted_data"
)
@patch.object(NagadPayment, "_generate_signature", return_value="dummy_signature")
@patch.object(NagadPayment, "_send_request", return_value={"status": "initiated"})
def test_initiate_payment(
    mock_send_request: MagicMock,
    mock_generate_signature: MagicMock,
    mock_encrypt_data: MagicMock,
    nagad_payment: NagadPayment,
) -> None:
    invoice_number = "INV12345"
    result = nagad_payment._initiate_payment(invoice_number)
    assert result == {"status": "initiated"}


@patch.object(
    NagadPayment, "_encrypt_data_using_public_key", return_value="dummy_encrypted_data"
)
@patch.object(NagadPayment, "_generate_signature", return_value="dummy_signature")
@patch.object(NagadPayment, "_send_request", return_value={"status": "completed"})
def test_complete_payment(
    mock_send_request: MagicMock,
    mock_generate_signature: MagicMock,
    mock_encrypt_data: MagicMock,
    nagad_payment: NagadPayment,
) -> None:
    amount = "100.00"
    invoice_number = "INV12345"
    challenge = "challenge123"
    payment_reference_id = "REF456"
    result = nagad_payment._complete_payment(
        amount, invoice_number, challenge, payment_reference_id
    )
    assert result == {"status": "completed"}


@patch.object(
    NagadPayment,
    "_initiate_payment",
    return_value={"sensitiveData": "dummy_sensitive_data=="},
)
@patch.object(
    NagadPayment,
    "_decrypt_data_using_private_key",
    return_value='{"paymentReferenceId": "123", "challenge": "abc"}',
)
@patch.object(NagadPayment, "_complete_payment", return_value={"status": "completed"})
def test_checkout_process(
    mock_complete_payment: MagicMock,
    mock_decrypt_data: MagicMock,
    mock_initiate_payment: MagicMock,
    nagad_payment: NagadPayment,
) -> None:
    amount = "100.00"
    invoice_number = "INV12345"
    result = nagad_payment.checkout_process(amount, invoice_number)
    assert result == {"status": "completed"}
