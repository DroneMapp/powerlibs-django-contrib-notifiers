from unittest import mock

import pytest

from tests.factories import CRUDNotifierModel, ChangeNotifierModel


@pytest.fixture
def mocked_notifier():
    return mock.Mock(
        notify=mock.Mock()
    )


@pytest.fixture
def crud_notifier_model(mocked_notifier):
    CRUDNotifierModel.notifiers = [mocked_notifier]
    return CRUDNotifierModel


@pytest.fixture
def change_notifier_model(mocked_notifier):
    ChangeNotifierModel.notifiers = [mocked_notifier]
    return ChangeNotifierModel
