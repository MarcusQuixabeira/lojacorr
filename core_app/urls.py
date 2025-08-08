from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

urlpatterns = [
    path('api/v1/insureds/', views.InsuredRegistrationView.as_view()),
    path('api/v1/insureds/<int:pk>/', views.InsuredEditView.as_view()),
    path('api/v1/login/', views.InsuredLoginView.as_view()),
]
