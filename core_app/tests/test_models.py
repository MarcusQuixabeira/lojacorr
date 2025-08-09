import time
from django.test import TestCase
from django.core.exceptions import ValidationError

from core_app.models import Insured

class InsuredModelTests(TestCase):
    def _make_insured(self, *, email='john@example.com', name='John Doe', cpf='52998224725', password='s3cr3t'):
        """Helper to create a valid Insured, running validators."""
        insured = Insured(email=email, name=name, cpf=cpf, password=password)
        insured.full_clean()
        insured.set_password(password)
        insured.save()
        return insured

    def test_create_insured_success(self):
        insured = self._make_insured()
        self.assertIsNotNone(insured.pk)
        self.assertTrue(insured.check_password('s3cr3t'))
        self.assertEqual(str(insured), 'John Doe')
        self.assertIsNotNone(insured.created_at)
        self.assertIsNotNone(insured.updated_at)

    def test_cpf_validator_blocks_invalid_cpf(self):
        insured = Insured(email='bad@example.com', name='Bad CPF', cpf='52998224724')
        with self.assertRaises(ValidationError):
            insured.full_clean()

    def test_email_unique_validation(self):
        self._make_insured(email='unique@example.com')
        dup = Insured(email='unique@example.com', name='Dup', cpf='52998224725')
        with self.assertRaises(ValidationError):
            dup.full_clean()

    def test_cpf_unique_validation(self):
        self._make_insured(email='unique@example.com', cpf='52998224725')
        dup = Insured(email='unique2@example.com', name='Dup', cpf='52998224725')
        with self.assertRaises(ValidationError):
            dup.full_clean()

    def test_updated_at_changes_on_save(self):
        insured = self._make_insured()
        first_updated = insured.updated_at
        time.sleep(0.05)
        insured.name = 'John Updated'
        insured.save()
        insured.refresh_from_db()
        self.assertGreaterEqual(insured.updated_at, first_updated)