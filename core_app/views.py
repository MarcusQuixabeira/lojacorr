from django.utils.timezone import now
from django.shortcuts import get_object_or_404

from drf_spectacular.utils import extend_schema, OpenApiExample
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import InsuredSerializer, InsuredLoginSerializer, InsuredEditSerializer
from .models import Insured
from .auth import InsuredJWTAuthentication


class InsuredLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Authentication"],
        auth=[],
        summary="Login of the Insured",
        description="Authenticates the Insured with his email and password, returning JWT tokens.",
        request=InsuredLoginSerializer,
        responses={
            200: InsuredLoginSerializer,
        },
        examples=[
            OpenApiExample(
                "Request example",
                value={
                    "email": "joao.silva@example.com",
                    "password": "safePassword123"
                },
                request_only=True
            ),
            OpenApiExample(
                "Response Example",
                value={
                    'refresh': 'jwt-refresh-token',
                    'access': 'jwt-access-token',
                    'insured_id': 1,
                    'email': 'joao.silva@example.com'
                },
                response_only=True
            ),
            OpenApiExample(
                "Error response example",
                value={"non_field_errors": ["E-mail or password are incorrect"]},
                response_only=True
            ),
        ]
    )
    def post(self, request):
        serializer = InsuredLoginSerializer(data=request.data)
        if serializer.is_valid():
            insured = serializer.validated_data['insured']
            insured.last_login = now()
            insured.save(update_fields=['last_login'])
            del serializer.validated_data['insured']
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class InsuredRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        tags=["Insured"],
        auth=[],
        summary="Insured Registration",
        description=(
            "Register a new Insured in the system.\n\n"
            "Rrequired fields:\n"
            "- **name**: Insured's full name\n"
            "- **email**: Insured's e-mail address\n"
            "- **cpf**: Insured's CPF, only numbers\n"
            "- **password**: The password\n\n"
            "The field `password` is write only and will be not be sent as response."
        ),
        request=InsuredSerializer,
        responses={
            200: InsuredSerializer,
        },
        examples=[
            OpenApiExample(
                "Request example",
                value={
                    "name": "João Silva",
                    "email": "joao.silva@example.com",
                    "cpf": "12345678900",
                    "password": "safePassword123"
                },
                request_only=True
            ),
            OpenApiExample(
                "Response Example",
                value={
                    "name": "João Silva",
                    "email": "joao.silva@example.com",
                    "cpf": "12345678900",
                    "created_at": "2025-08-08T14:35:00Z",
                    "updated_at": "2025-08-08T14:35:00Z"
                },
                response_only=True
            ),
            OpenApiExample(
                "Error response example",
                value={
                    "email": ["Email already exists."]
                },
                response_only=True
            )
        ]
    )
    def post(self, request):
        serializer = InsuredSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InsuredEditView(APIView):
    authentication_classes = [InsuredJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Insured"],
        auth=[{"BearerAuth": []}],
        summary="Update insured data",
        description=(
            "Allows an authenticated insured user to update their personal data, such as name and password.\n\n"
            "The `password_confirmation` field must match the `password` field.\n"
            "All fields are required.\n\n"
            "**JWT authentication is required** (use `Authorization: Bearer <token>`)."
        ),
        request=InsuredEditSerializer,
        responses={
            200: InsuredSerializer,
            400: OpenApiExample(
                'Validation error',
                value={"password": ["This field is required."]}
            ),
        },
        examples=[
            OpenApiExample(
                "Example request to update insured",
                value={
                    "name": "Updated Name",
                    "password": "newsecurepassword",
                    "password_confirmation": "newsecurepassword"
                },
                request_only=True
            ),
            OpenApiExample(
                "Example successful response",
                value={
                    "name": "Updated Name",
                    "email": "john@example.com",
                    "cpf": "12345678900",
                    "created_at": "2025-08-08T14:35:00Z",
                    "updated_at": "2025-08-08T15:20:00Z"
                },
                response_only=True
            )
        ]
    )
    def patch(self, request, pk):
        serializer = InsuredEditSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            insured = get_object_or_404(Insured, pk=pk)
            password = serializer.validated_data.pop('password', None)
            for attr, value in serializer.validated_data.items():
                setattr(insured, attr, value)
            if password:
                insured.set_password(password)
            insured.save()
            return Response(InsuredSerializer(insured).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)