from collections.abc import Iterable

from django.utils import timezone

import graphene
from graphene_django import DjangoObjectType

from ..models import PersonalEvent
from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    PermissionBatchPatchMixin,
)


class PersonalEventType(DjangoObjectType):
    class Meta:
        model = PersonalEvent
        fields = (
            "id",
            "title",
            "description",
            "location",
            "datetime_start",
            "datetime_end",
            "date_start",
            "date_end",
            "owner",
            "persons",
            "groups",
        )

    timezone = graphene.String()
    recurrences = graphene.String()


class PersonalEventBatchCreateMutation(PermissionBatchPatchMixin, BaseBatchCreateMutation):
    class Meta:
        model = PersonalEvent
        permissions = ("core.create_personal_event_with_invitations_rule",)
        only_fields = (
            "title",
            "description",
            "location",
            "datetime_start",
            "datetime_end",
            "timezone",
            "date_start",
            "date_end",
            "recurrences",
            "persons",
            "groups",
        )
        field_types = {
            "timezone": graphene.String(),
            "recurrences": graphene.String(),
            "location": graphene.String(),
        }
        optional_fields = ("timezone", "recurrences")

    @classmethod
    def get_permissions(cls, root, info, input) -> Iterable[str]:  # noqa
        if [len(event.persons) == 0 and len(event.groups) == 0 for event in input].all():
            return ("core.create_personal_event_rule",)
        return cls._meta.permissions

    @classmethod
    def before_mutate(cls, root, info, input):  # noqa
        for event in input:
            event["owner"] = info.context.user.person.id
        return input

    @classmethod
    def handle_datetime_start(cls, value, name, info):
        value = value.replace(tzinfo=timezone.get_default_timezone())
        return value

    @classmethod
    def handle_datetime_end(cls, value, name, info):
        value = value.replace(tzinfo=timezone.get_default_timezone())
        return value


class PersonalEventBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = PersonalEvent
        permissions = ("core.delete_personal_event_rule",)


class PersonalEventBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = PersonalEvent
        permissions = ("core.change_personalevent",)
        only_fields = (
            "id",
            "title",
            "description",
            "location",
            "datetime_start",
            "datetime_end",
            "timezone",
            "date_start",
            "date_end",
            "recurrences",
            "persons",
            "groups",
        )
        field_types = {
            "timezone": graphene.String(),
            "recurrences": graphene.String(),
            "location": graphene.String(),
        }
        optional_fields = ("timezone", "recurrences")

    @classmethod
    def get_permissions(cls, root, info, input, id, obj) -> Iterable[str]:  # noqa
        if info.context.user.has_perm("core.edit_personal_event_rule", obj):
            return []
        return cls._meta.permissions

    @classmethod
    def before_mutate(cls, root, info, input):  # noqa
        for event in input:
            # Remove recurrences if none were received.
            if "recurrences" not in event:
                event["recurrences"] = ""

        return input
