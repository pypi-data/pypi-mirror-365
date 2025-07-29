from django.urls import path
from dj_notify.views import whatsapp_webhook

urlpatterns = [
    path('webhook/whatsapp/', whatsapp_webhook, name='whatsapp_webhook'),
]
