from django.utils.timezone import now

from drf_spectacular.utils import extend_schema, OpenApiExample, OpenApiResponse
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
            "Required fields:\n"
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
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InsuredEditView(APIView):
    authentication_classes = [InsuredJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(
        tags=["Insured"],
        summary="Edit insured profile (partial update)",
        description=(
            "Partially updates the authenticated insured profile. "
            "You can update the **name** and optionally change the **password**.\n\n"
            "**Rules:**\n"
            "- To change password, both `password` and `password_confirmation` must be provided.\n"
            "- `password` and `password_confirmation` must match.\n"
            "- If you send empty strings for the password fields, the password is ignored."
        ),
        request=InsuredEditSerializer,
        responses={
            200: OpenApiResponse(response=InsuredSerializer, description="Updated insured profile"),
            400: OpenApiResponse(description="Validation error"),
        },
        examples=[
            OpenApiExample(
                "Update name only",
                request_only=True,
                value={"name": "John Updated", "password": "", "password_confirmation": ""}
            ),
            OpenApiExample(
                "Change password (and name)",
                request_only=True,
                value={"name": "John Doe", "password": "newpass123", "password_confirmation": "newpass123"}
            ),
            OpenApiExample(
                "Success response",
                response_only=True,
                value={
                    "name": "John Updated",
                    "email": "john@example.com",
                    "cpf": "52998224725",
                    "created_at": "2025-08-08T14:35:00Z",
                    "updated_at": "2025-08-08T14:36:11Z"
                }
            ),
            OpenApiExample(
                "Error: passwords mismatch",
                response_only=True,
                status_codes=["400"],
                value={"non_field_errors": ["password and password confirmation needs to be the same"]}
            ),
            OpenApiExample(
                "Error: only one password field informed",
                response_only=True,
                status_codes=["400"],
                value={"non_field_errors": ["password and password needs to be both informed."]}
            ),
        ],
    )
    def patch(self, request):
        serializer = InsuredEditSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            insured = Insured.objects.filter(pk=request.user.pk).first()
            if not insured:
                return Response(serializer.errors, status=status.HTTP_401_UNAUTHORIZED)
            password = serializer.validated_data.pop('password', None)
            for attr, value in serializer.validated_data.items():
                setattr(insured, attr, value)
            if password:
                insured.set_password(password)
            insured.save()
            return Response(InsuredSerializer(insured).data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)