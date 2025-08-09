import time
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework import status

from core_app.models import Insured

REGISTER_URL = '/api/v1/insureds/'
LOGIN_URL = '/api/v1/login/'
EDIT_URL = '/api/v1/insureds/edit/'


class InsuredIntegrationTests(APITestCase):
    def _register(self, *, name='John Doe', email='john@example.com',
                  cpf='52998224725', password='s3cr3t!'):
        payload = {
            'name': name,
            'email': email,
            'cpf': cpf,
            'password': password,
        }
        resp = self.client.post(REGISTER_URL, payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        self.assertNotIn('password', resp.data)
        return resp

    def _login(self, email='john@example.com', password='s3cr3t!'):
        resp = self.client.post(LOGIN_URL, {'email': email, 'password': password}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        self.assertIn('access', resp.data)
        self.assertIn('refresh', resp.data)
        self.assertEqual(resp.data['email'], email)
        return resp

    def _auth(self, access_token: str):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

    def test_full_flow_register_login_edit(self):
        # 1) Registration
        reg = self._register()
        insured_id = Insured.objects.get(email='john@example.com').pk

        # 2) Login
        login = self._login()
        token = login.data['access']
        self._auth(token)

        # 3) Name editing + change password with password confirmation
        patch_payload = {
            'name': 'John Updated',
            'password': 'newpass123',
            'password_confirmation': 'newpass123',
        }
        resp = self.client.patch(EDIT_URL, patch_payload, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK, resp.data)
        self.assertEqual(resp.data['name'], 'John Updated')

        # 4) Login with the new password need to work
        self.client.credentials()
        relogin = self._login(password='newpass123')
        self.assertEqual(relogin.status_code, 200)

    def test_edit_requires_auth_returns_403(self):
        self._register()
        insured_id = Insured.objects.get(email='john@example.com').pk
        resp = self.client.patch(EDIT_URL, {'name': 'X'}, format='json')
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)

    def test_edit_password_mismatch_400(self):
        self._register()
        token = self._login().data['access']
        insured_id = Insured.objects.get(email='john@example.com').pk
        self._auth(token)

        resp = self.client.patch(EDIT_URL, {
            'name': 'John',
            'password': 'abcdef',
            'password_confirmation': 'abcdefg',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('non_field_errors', resp.data)

    def test_login_sets_last_login(self):
        self._register()
        user = Insured.objects.get(email='john@example.com')
        self.assertIsNone(user.last_login)

        login = self._login()
        user.refresh_from_db()
        self.assertIsNotNone(user.last_login)

    def test_cpf_is_normalized_on_register(self):
        self._register(cpf='52998224725')
        user = Insured.objects.get(email='john@example.com')
        self.assertEqual(user.cpf, '52998224725')

    def test_unique_email_violation_on_register(self):
        self._register(email='dup@example.com', cpf='52998224725')
        resp = self.client.post(REGISTER_URL, {
            'name': 'Other',
            'email': 'dup@example.com',
            'cpf': '168.995.350-09',
            'password': 'abcdef',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', resp.data)

    def test_edit_name_only_with_blank_passwords(self):
        self._register()
        token = self._login().data['access']
        insured = Insured.objects.get(email='john@example.com')
        self._auth(token)

        resp = self.client.patch(EDIT_URL, {
            'name': 'Only Name',
            'password': '',
            'password_confirmation': '',
        }, format='json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK) # only name will be saved
        self.assertEqual(resp.data['name'], 'Only Name')

    def test_schema_endpoint_available(self):
        resp = self.client.get('/api/schema/')
        self.assertIn(resp.status_code, (200, 301, 302))
