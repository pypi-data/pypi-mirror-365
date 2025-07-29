from django.urls import path, include

urlpatterns = [
    path('whatsapp/', include('nic_notify.whatsapp.urls')),
    path('email/', include('nic_notify.email.urls')),
]
