from django.urls import path

from payments.views import merchants

urlpatterns = [
    path('<int:id>/balance', merchants.balance),
    path('<int:id>/report', merchants.report),
]
