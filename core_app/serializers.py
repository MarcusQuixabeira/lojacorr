import re

from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Insured
from .validators import validate_cpf


class InsuredSerializer(serializers.ModelSerializer):
    class Meta:
        model = Insured
        fields = ['name', 'email', 'cpf', 'created_at', 'updated_at', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def validate_cpf(self, value):
        digits = re.sub(r'\D', '', value or '')
        validate_cpf(digits)
        return digits

    def create(self, validated_data):
        password = validated_data.pop('password')
        insured = Insured(**validated_data)
        insured.set_password(password)
        insured.save()
        return insured


class InsuredEditSerializer(serializers.Serializer):
    name = serializers.CharField(allow_blank=False)
    password = serializers.CharField(min_length=6, allow_blank=True)
    password_confirmation = serializers.CharField(min_length=6, allow_blank=True)
    
    def validate(self, data):
        name = data.get("name")
        password = data.get("password")
        password_confirmation = data.get("password_confirmation")
        
        result = {'name': name}
        
        if password and not password_confirmation or password_confirmation and not password:
            raise serializers.ValidationError("password and password needs to be both informed.")
        
        if password and password_confirmation:
            if not password == password_confirmation:
                raise serializers.ValidationError("password and password confirmation needs to be the same")
            result['password'] = password

        return result

class InsuredLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")

        try:
            insured = Insured.objects.get(email=email)
        except Insured.DoesNotExist:
            raise serializers.ValidationError("E-mail or password are incorrect")

        if not insured.check_password(password):
            raise serializers.ValidationError("E-mail or password are incorrect")

        refresh = RefreshToken.for_user(insured)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'insured': insured,
            'insured_id': insured.pk,
            'email': insured.email,
        }