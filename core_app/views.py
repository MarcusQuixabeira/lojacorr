from django.utils.timezone import now
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions

from .serializers import InsuredSerializer, InsuredLoginSerializer, InsuredEditSerializer
from .models import Insured
from .auth import InsuredJWTAuthentication



class InsuredRegistrationView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = InsuredSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InsuredLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = InsuredLoginSerializer(data=request.data)
        if serializer.is_valid():
            insured = serializer.validated_data['insured']
            insured.last_login = now()
            insured.save(update_fields=['last_login'])
            del serializer.validated_data['insured']
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InsuredEditView(APIView):
    authentication_classes = [InsuredJWTAuthentication]
    permission_classes = [permissions.IsAuthenticated]

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