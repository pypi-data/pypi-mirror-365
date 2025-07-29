from django.urls import path, include

urlpatterns = [
    path('whatsapp/', include('notify_service.whatsapp.urls')),
    path('email/', include('notify_service.email.urls')),
]
