from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from setup.settings import SECRET_KEY
from .models import Insured
import jwt

class InsuredJWTAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            _, token = auth_header.split(' ')
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except Exception:
            raise AuthenticationFailed('Invalid Token')

        try:
            insured = Insured.objects.get(pk=payload['user_id'])
        except Insured.DoesNotExist:
            raise AuthenticationFailed('Insured not found')
        
        return (insured, None)