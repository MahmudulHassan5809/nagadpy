from unittest.mock import Mock, patch

import pytest
from nagadpy.exceptions import PaymentVerificationError
from nagadpy.payment_verify import NagadPaymentVerify


@pytest.fixture
def nagad_payment_verify() -> NagadPaymentVerify:
    return NagadPaymentVerify(base_url="https://example.com")


@patch("requests.get")
def test_verify_payment_successful(
    mock_get: Mock, nagad_payment_verify: NagadPaymentVerify
) -> None:
    response_data = {"status": "success"}
    mock_response = Mock()
    mock_response.json.return_value = response_data
    mock_get.return_value = mock_response

    payment_reference_id = "REF456789"

    result = nagad_payment_verify.verify_payment(payment_reference_id)

    assert result == response_data
    expected_url = "https://example.com/verify/payment/REF456789"
    mock_get.assert_called_once_with(expected_url)


@patch("requests.get")
def test_verify_payment_request_error(
    mock_get: Mock, nagad_payment_verify: NagadPaymentVerify
) -> None:
    mock_get.side_effect = Exception("Request error")

    payment_reference_id = "REF456789"

    with pytest.raises(PaymentVerificationError) as exc_info:
        nagad_payment_verify.verify_payment(payment_reference_id)
    assert "Request error" in str(exc_info.value)
