from rest_framework.authentication import BaseAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from decouple import config
from .models import Insured
import jwt

class InsuredJWTAuthentication(BaseAuthentication):
    keyword = b'Bearer'
    def authenticate(self, request):
        parts = get_authorization_header(request).split()

        if not parts:
            return None
        if parts[0].lower() != self.keyword.lower():
            return None
        if len(parts) == 1:
            raise AuthenticationFailed('Invalid Authorization header. No credentials provided.')
        if len(parts) > 2:
            raise AuthenticationFailed('Invalid Authorization header. Too many spaces.')

        token = parts[1]

        signing_key = config('JWT_SECRET')
        algorithms = config('JWT_ALGORITHM')

        try:
            payload = jwt.decode(token, signing_key, algorithms=algorithms)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')

        if payload.get('token_type') and payload['token_type'] != 'access':
            raise AuthenticationFailed('Use an access token.')

        user_id = payload.get('user_id') or payload.get('sub')
        if not user_id:
            raise AuthenticationFailed('Invalid token payload.')

        try:
            insured = Insured.objects.get(pk=user_id)
        except Insured.DoesNotExist:
            raise AuthenticationFailed('Insured not found.')

        return (insured, None)