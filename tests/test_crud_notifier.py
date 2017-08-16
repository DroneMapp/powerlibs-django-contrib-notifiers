import pytest


pytestmark = pytest.mark.django_db


def test_CRUDNotifierModel_creation(mocked_notifier, crud_notifier_model):
    instance = crud_notifier_model(name='creation test')
    instance.save()

    assert mocked_notifier.notify.call_count == 1

    args, kwargs = mocked_notifier.notify.call_args
    topic, data = args

    assert topic == 'crud_notifier_model__created'
    assert data['id'] == instance.id
    assert data['name'] == 'creation test'


def test_CRUDNotifierModel_update(mocked_notifier, crud_notifier_model):
    instance = crud_notifier_model(name='creation test')
    instance.save()

    instance.name = 'new name'
    instance.save()

    assert mocked_notifier.notify.call_count == 2

    args, kwargs = mocked_notifier.notify.call_args
    topic, data = args

    assert topic == 'crud_notifier_model__updated'
    assert data['id'] == instance.id
    assert data['name'] == 'new name'


def test_CRUDNotifierModel_deletion(mocked_notifier, crud_notifier_model):
    instance = crud_notifier_model(name='creation test')
    instance.save()
    instance.delete()
    assert mocked_notifier.notify.call_count == 2

    args, kwargs = mocked_notifier.notify.call_args
    topic, data = args

    assert topic == 'crud_notifier_model__deleted'
