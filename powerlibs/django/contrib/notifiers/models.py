import re

from powerlibs.string_utils import snake_case
from powerlibs.django.contrib.eventful.models import EventfulModelMixin


class NotifierMixin(EventfulModelMixin):
    notifiers = []

    @property
    def notification_prefixes(self):
        return [snake_case(type(self).__name__)]

    def notify(self, topic, message=None):
        message = message or self.serialize()
        for prefix in self.notification_prefixes:
            prefixed_topic = '{}__{}'.format(prefix, topic)
            for notifier in self.notifiers:
                notifier.notify(prefixed_topic, message)


class CRUDNotifierMixin(NotifierMixin):
    def post_creation_crud_notifier(self, **context):
        self.notify('created')

    def post_update_crud_notifier(self, **context):
        self.notify('updated')

    def post_delete_crud_notifier(self, **context):
        self.notify('deleted')


class ChangeNotifierMixin(NotifierMixin):
    notable_fields = ['status']

    def retrieve_itself_from_database(self):  # pragma: no cover
        return type(self).objects.get(pk=self.pk)

    def pre_creation_change_notifier(self, **context):
        self._notable_fields_values = dict((field_name, None) for field_name in self.notable_fields)

    def post_creation_change_notifier(self, **context):
        return self.post_update_change_notifier(**context)

    def pre_update_change_notifier(self, **context):
        old_object = self.retrieve_itself_from_database()

        self._notable_fields_values = {}
        for field_name in self.notable_fields:
            value = getattr(old_object, field_name)
            self._notable_fields_values[field_name] = value

    def get_safe_value_for_status_notification(self, new_value):
        if isinstance(new_value, bool):
            safe_value = 'true' if new_value else 'false'
        elif new_value == '':
            safe_value = 'blank'
        else:
            safe_value = re.sub(r'[^a-z0-9_]+', '_', str(new_value).lower())

        return safe_value

    def get_topic_name_for_status_notification(self, field_name, safe_value):
        if field_name == 'status':
            if isinstance(self, CRUDNotifierMixin) and safe_value in ('created', 'updated', 'deleted'):
                return
            topic_name = safe_value
        else:
            topic_name = "{}__{}".format(field_name, safe_value)

        return topic_name

    def post_update_change_notifier(self, **context):
        for field_name, old_value in self._notable_fields_values.items():
            new_value = getattr(self, field_name)
            if new_value != old_value:

                safe_value = self.get_safe_value_for_status_notification(new_value)
                topic_name = self.get_topic_name_for_status_notification(field_name, safe_value)

                if topic_name:
                    message = self.serialize()
                    message['_old_value'] = old_value
                    message['_changed_field'] = field_name

                    self.notify(topic_name, message)


class SoftDeletionNotifier:
    def post_update_crud_notifier(self, **context):
        if self.deleted is True:
            self.notify('soft_deleted')
        else:
            self.notify('updated')

    def serialize(self):
        data = super().serialize()
        if 'deleted' in data:
            del data['deleted']
        return data
