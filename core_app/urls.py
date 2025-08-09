from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from . import views

urlpatterns = [
    path('api/v1/insureds/', views.InsuredRegistrationView.as_view()),
    path('api/v1/insureds/edit/', views.InsuredEditView.as_view()),
    path('api/v1/login/', views.InsuredLoginView.as_view()),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),

    path('api/docs/swagger/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),

    path('api/docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
