class PaymentVerificationError(Exception):
    """
    Custom exception for errors encountered during payment verification.

    This exception is raised when there is an issue with verifying a payment.

    Attributes:
        message (str): A human-readable error message describing the exception.
    """

    pass


class SignatureGenerationError(Exception):
    """
    Custom exception for errors encountered during signature generation.

    This exception is raised when there is an issue with generating digital signatures.

    Attributes:
        message (str): A human-readable error message describing the exception.
    """

    pass


class EncryptionError(Exception):
    """
    Custom exception for errors encountered during data encryption.

    This exception is raised when there is an issue with encrypting sensitive data.

    Attributes:
        message (str): A human-readable error message describing the exception.
    """

    pass


class DecryptionError(Exception):
    """
    Custom exception for errors encountered during data decryption.

    This exception is raised when there is an issue with decrypting encrypted data.

    Attributes:
        message (str): A human-readable error message describing the exception.
    """

    pass


class RequestError(Exception):
    """
    Custom exception for errors encountered during HTTP requests.

    This exception is raised when there is an issue with making HTTP requests.

    Attributes:
        message (str): A human-readable error message describing the exception.
    """

    pass


class PaymentInitiationError(Exception):
    """
    Custom exception for errors encountered during payment initiation.

    This exception is raised when there is an issue with initiating a payment.

    Attributes:
        message (str): A human-readable error message describing the exception.
    """

    pass


class PaymentCompleteError(Exception):
    """
    Custom exception for errors encountered during payment completion.

    This exception is raised when there is an issue with completing a payment.

    Attributes:
        message (str): A human-readable error message describing the exception.
    """

    pass


class CheckProcessError(Exception):
    """
    Custom exception for errors encountered during the payment process.

    This exception is raised when there is an issue with any step of the payment process.

    Attributes:
        message (str): A human-readable error message describing the exception.
    """

    pass
