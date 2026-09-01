import pytest

from payments.models import Merchant, MerchantStatus, Project


@pytest.fixture(autouse=True, scope='session')
def set_up(django_db_setup, django_db_blocker):
    with django_db_blocker.unblock():
        merchant = Merchant(name='merchant-test', status=MerchantStatus.ACTIVE)
        project = Project(
            name='project-test',
            webhook_url='http://test.host/hook',
            webhook_secret='secret',
            merchant=merchant,
        )

        merchant.save()
        project.save()
