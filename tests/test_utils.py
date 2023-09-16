import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))


from nagadpy.utils import generate_challenge, get_timestamp


class TestUtils:
    def test_generate_challenge_returns_string(self):
        result = generate_challenge(40)
        assert isinstance(result, str), "Generated challenge should be a string"

    def test_generate_challenge_has_correct_length(self):
        length = 40
        result = generate_challenge(length)
        assert len(result) == length, f"Generated challenge length should be {length}"

    def test_generate_challenge_contains_only_lowercase_letters(self):
        result = generate_challenge(40)
        assert (
            result.islower()
        ), "Generated challenge should contain only lowercase letters"

    def test_get_timestamp_returns_string(self):
        result = get_timestamp()
        assert isinstance(result, str), "Timestamp should be a string"

    def test_get_timestamp_has_correct_length(self):
        result = get_timestamp()
        assert len(result) == 14, "Timestamp length should be 14 characters"

    def test_get_timestamp_contains_only_digits(self):
        result = get_timestamp()
        assert result.isdigit(), "Timestamp should contain only digits"
