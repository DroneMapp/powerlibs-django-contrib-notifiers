from unittest import mock
import pytest


pytestmark = pytest.mark.django_db


def test_ChangeNotifierModel_status_change(mocked_notifier, change_notifier_model):
    # Create:
    instance = change_notifier_model(name='test 01')
    instance.save()

    assert mocked_notifier.notify.call_count == 1

    # Update:
    old_value = instance.status
    instance.status = 'status 2'
    instance.save()

    assert instance.debug_info['pre_creation_handler_called'] == 1
    assert instance.debug_info['post_creation_handler_called'] == 1
    assert instance.debug_info['pre_update_handler_called'] == 1
    assert instance.debug_info['post_update_handler_called'] == 1
    assert instance.debug_info['pre_delete_handler_called'] == 0
    assert instance.debug_info['post_delete_handler_called'] == 0

    assert mocked_notifier.notify.call_count == 2

    args, kwargs = mocked_notifier.notify.call_args
    topic, data = args

    assert topic == 'change_notifier_model__status_2'
    assert data['id'] == instance.pk
    assert data['_old_value'] == old_value


def test_ChangeNotifierModel_activation_change(mocked_notifier, change_notifier_model):
    # Create:
    instance = change_notifier_model(name='test changing activation data')
    instance.save()

    assert mocked_notifier.notify.call_count == 1

    # Update:
    old_value = instance.activated
    instance.activated = True
    instance.save()

    assert mocked_notifier.notify.call_count == 2

    args, kwargs = mocked_notifier.notify.call_args
    topic, data = args

    assert topic == 'change_notifier_model__activated__true'
    assert data['id'] == instance.pk
    assert data['_old_value'] == old_value


# def test_ChangeNotifierModel_activation_change_when_notification_for_topic_is_canceled(mocked_notifier, change_notifier_model):
#     # Create:
#     instance = change_notifier_model(name='test changing activation data')
#     instance.get_topic_name_for_status_notification = mock.Mock(return_value=None)
#     instance.save()
#
#     assert mocked_notifier.notify.call_count == 0
#
#     # Update:
#     instance.activated = True
#     instance.save()
#
#     assert mocked_notifier.notify.call_count == 0


def test_change_notifier_with_blank_value(mocked_notifier, change_notifier_model):
    blank_instance = change_notifier_model(name='', status='')
    blank_instance.save()

    topics = tuple(args[0] for args, kwargs in mocked_notifier.notify.call_args_list)
    assert 'change_notifier_model__blank' in topics

    """
    ('change_notifier_model__blank', 'change_notifier_model__activated__false')
    """
    assert mocked_notifier.notify.call_count == 2
