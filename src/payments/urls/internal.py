from django.urls import path

from payments.views import internal

urlpatterns = [
    path('payments', internal.payments),
]
