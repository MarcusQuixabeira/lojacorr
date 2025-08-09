from django.test import SimpleTestCase, TestCase
from django.core.exceptions import ValidationError

from core_app.validators import validate_cpf


class ValidateCPFTests(SimpleTestCase):
    def test_valid_cpf_without_mask(self):
        self.assertIsNone(validate_cpf('52998224725'))

    def test_valid_cpf_with_mask(self):
        self.assertIsNone(validate_cpf('529.982.247-25'))

    def test_cpf_with_spaces_or_punctuation(self):
        self.assertIsNone(validate_cpf(' 529 982 247 25 '))

    def test_invalid_length(self):
        with self.assertRaises(ValidationError):
            validate_cpf('1234567890')

    def test_repeated_sequence(self):
        with self.assertRaises(ValidationError):
            validate_cpf('11111111111')

    def test_invalid_check_digits(self):
        with self.assertRaises(ValidationError):
            validate_cpf('529.982.247-24')

    def test_empty_or_none(self):
        with self.assertRaises(ValidationError):
            validate_cpf('')
        with self.assertRaises(ValidationError):
            validate_cpf(None)