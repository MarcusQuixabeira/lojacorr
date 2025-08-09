from django.test import SimpleTestCase, TestCase

from core_app.models import Insured
from core_app.serializers import (
    InsuredSerializer,
    InsuredEditSerializer,
    InsuredLoginSerializer,
)

class InsuredSerializerTests(TestCase):
    def test_invalid_cpf_raises_error(self):
        payload = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "cpf": "529.982.247-24",  # invalid DV
            "password": "abcdef",
        }
        serializer = InsuredSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        # error likely on "cpf"
        self.assertIn("cpf", serializer.errors)

    def test_unique_email_validation(self):
        Insured.objects.create(
            email="dup@example.com", name="Dup1", cpf="52998224725"
        ).set_password("abc123")  # set_password then save again to persist hash
        # Need to persist the hash write:
        i = Insured.objects.get(email="dup@example.com")
        i.set_password("abc123")
        i.save()

        payload = {
            "name": "Dup2",
            "email": "dup@example.com",  # duplicate
            "cpf": "168.995.350-09",     # another valid CPF
            "password": "abcdef",
        }
        serializer = InsuredSerializer(data=payload)
        self.assertFalse(serializer.is_valid())
        self.assertIn("email", serializer.errors)

    def test_password_is_write_only_in_representation(self):
        payload = {
            "name": "John Doe",
            "email": "john2@example.com",
            "cpf": "52998224725",
            "password": "secret123",
        }
        s = InsuredSerializer(data=payload)
        self.assertTrue(s.is_valid(), s.errors)
        instance = s.save()
        rep = InsuredSerializer(instance).data
        self.assertNotIn("password", rep)


class InsuredEditSerializerTests(SimpleTestCase):
    def test_update_name_only_with_blank_passwords(self):
        data = {
            "name": "John Updated",
            "password": "",
            "password_confirmation": "",
        }
        s = InsuredEditSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        validated = s.validated_data
        self.assertEqual(validated["name"], "John Updated")
        self.assertNotIn("password", validated)

    def test_error_when_only_password_provided(self):
        data = {
            "name": "John",
            "password": "abcdef",
            "password_confirmation": "",
        }
        s = InsuredEditSerializer(data=data)
        self.assertFalse(s.is_valid())
        # custom message from validate()
        self.assertIn("non_field_errors", s.errors)
        self.assertIn("password and password needs to be both informed.", s.errors["non_field_errors"])

    def test_error_when_only_password_confirmation_provided(self):
        data = {
            "name": "John",
            "password": "",
            "password_confirmation": "abcdef",
        }
        s = InsuredEditSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("non_field_errors", s.errors)
        self.assertIn("password and password needs to be both informed.", s.errors["non_field_errors"])

    def test_error_when_passwords_mismatch(self):
        data = {
            "name": "John",
            "password": "abcdef",
            "password_confirmation": "abcdefg",
        }
        s = InsuredEditSerializer(data=data)
        self.assertFalse(s.is_valid())
        self.assertIn("non_field_errors", s.errors)
        self.assertIn("password and password confirmation needs to be the same", s.errors["non_field_errors"])

    def test_success_when_passwords_match(self):
        data = {
            "name": "John",
            "password": "abcdef",
            "password_confirmation": "abcdef",
        }
        s = InsuredEditSerializer(data=data)
        self.assertTrue(s.is_valid(), s.errors)
        self.assertEqual(s.validated_data["name"], "John")
        self.assertEqual(s.validated_data["password"], "abcdef")


class InsuredLoginSerializerTests(TestCase):
    def setUp(self):
        self.insured = Insured(email="login@example.com", name="Login User", cpf="52998224725")
        self.insured.set_password("s3cr3t")
        self.insured.save()

    def test_login_success_returns_tokens_and_user_info(self):
        s = InsuredLoginSerializer(data={"email": "login@example.com", "password": "s3cr3t"})
        self.assertTrue(s.is_valid(), s.errors)

        data = s.validated_data
        # must include tokens and user info
        for key in ("access", "refresh", "insured", "insured_id", "email"):
            self.assertIn(key, data)

        self.assertEqual(data["email"], "login@example.com")
        self.assertEqual(data["insured_id"], self.insured.pk)
        self.assertIsInstance(data["insured"], Insured)
        self.assertTrue(isinstance(data["access"], str) and data["access"])
        self.assertTrue(isinstance(data["refresh"], str) and data["refresh"])

    def test_login_invalid_email(self):
        s = InsuredLoginSerializer(data={"email": "nope@example.com", "password": "any"})
        self.assertFalse(s.is_valid())
        self.assertIn("non_field_errors", s.errors)
        self.assertIn("E-mail or password are incorrect", s.errors["non_field_errors"])

    def test_login_wrong_password(self):
        s = InsuredLoginSerializer(data={"email": "login@example.com", "password": "wrong"})
        self.assertFalse(s.is_valid())
        self.assertIn("non_field_errors", s.errors)
        self.assertIn("E-mail or password are incorrect", s.errors["non_field_errors"])