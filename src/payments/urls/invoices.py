from django.urls import path

from payments.views import invoices


urlpatterns = [
    path('', invoices.create),
    path('<int:id>', invoices.get_by_id),
    path('<int:id>/cancel', invoices.cancel)
]
