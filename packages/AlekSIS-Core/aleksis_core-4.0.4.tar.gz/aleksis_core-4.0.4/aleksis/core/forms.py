from collections.abc import Sequence
from typing import Any, Callable

from django import forms
from django.conf import settings
from django.contrib.auth.models import Permission
from django.core.exceptions import SuspiciousOperation, ValidationError
from django.db.models import QuerySet
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _

from allauth.account.adapter import get_adapter
from allauth.account.forms import SignupForm
from allauth.account.utils import setup_user_email
from django_select2.forms import ModelSelect2MultipleWidget, ModelSelect2Widget
from dynamic_preferences.forms import PreferenceForm
from guardian.shortcuts import assign_perm
from invitations.forms import InviteForm
from maintenance_mode.core import get_maintenance_mode
from material import Fieldset, Layout, Row

from .mixins import ExtensibleForm, SchoolTermRelatedExtensibleForm
from .models import (
    DashboardWidget,
    Group,
    Person,
    PersonInvitation,
)
from .registries import (
    group_preferences_registry,
    person_preferences_registry,
    site_preferences_registry,
)
from .util.core_helpers import get_site_preferences, queryset_rules_filter


class EditGroupForm(SchoolTermRelatedExtensibleForm):
    """Form to edit an existing group in the frontend."""

    layout = Layout(
        Fieldset(_("School term"), "school_term"),
        Fieldset(_("Common data"), "name", "short_name", "group_type"),
        Fieldset(_("Persons"), "members", "owners", "parent_groups"),
        Fieldset(_("Photo"), "photo", "avatar"),
    )

    class Meta:
        model = Group
        fields = [
            "school_term",
            "name",
            "short_name",
            "group_type",
            "members",
            "owners",
            "parent_groups",
            "photo",
            "avatar",
        ]
        widgets = {
            "members": ModelSelect2MultipleWidget(
                search_fields=[
                    "first_name__icontains",
                    "last_name__icontains",
                    "short_name__icontains",
                ],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "owners": ModelSelect2MultipleWidget(
                search_fields=[
                    "first_name__icontains",
                    "last_name__icontains",
                    "short_name__icontains",
                ],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
            "parent_groups": ModelSelect2MultipleWidget(
                search_fields=["name__icontains", "short_name__icontains"],
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            ),
        }


class ChildGroupsForm(forms.Form):
    """Inline form for group editing to select child groups."""

    child_groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all())


class SitePreferenceForm(PreferenceForm):
    """Form to edit site preferences."""

    registry = site_preferences_registry


class PersonPreferenceForm(PreferenceForm):
    """Form to edit preferences valid for one person."""

    registry = person_preferences_registry


class GroupPreferenceForm(PreferenceForm):
    """Form to edit preferences valid for members of a group."""

    registry = group_preferences_registry


class DashboardWidgetOrderForm(ExtensibleForm):
    pk = forms.ModelChoiceField(
        queryset=None,
        widget=forms.HiddenInput(attrs={"class": "pk-input"}),
    )
    order = forms.IntegerField(initial=0, widget=forms.HiddenInput(attrs={"class": "order-input"}))

    class Meta:
        model = DashboardWidget
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set queryset here to prevent problems with not migrated database due to special queryset
        self.fields["pk"].queryset = DashboardWidget.objects.all()


DashboardWidgetOrderFormSet = forms.formset_factory(
    form=DashboardWidgetOrderForm, max_num=0, extra=0
)


class InvitationCodeForm(forms.Form):
    """Form to enter an invitation code."""

    code = forms.CharField(
        label=_("Invitation code"),
        help_text=_("Please enter your invitation code."),
    )


class PersonCreateInviteForm(InviteForm):
    """Custom form to create a person and invite them."""

    first_name = forms.CharField(label=_("First name"), required=True)
    last_name = forms.CharField(label=_("Last name"), required=True)

    layout = Layout(
        Row("first_name", "last_name"),
        Row("email"),
    )

    def clean_email(self):
        if Person.objects.filter(email=self.cleaned_data["email"]).exists():
            raise ValidationError(_("A person is using this e-mail address"))
        return super().clean_email()

    def save(self, email):
        person = Person.objects.create(
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            email=email,
        )
        return PersonInvitation.create(email=email, person=person)


class SelectPermissionForm(forms.Form):
    """Select a permission to assign."""

    selected_permission = forms.ModelChoiceField(
        queryset=Permission.objects.all(),
        widget=ModelSelect2Widget(
            search_fields=["name__icontains", "codename__icontains"],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
    )


class AssignPermissionForm(forms.Form):
    """Assign a permission to user/groups for all/some objects."""

    layout = Layout(
        Fieldset(_("Who should get the permission?"), "groups", "persons"),
        Fieldset(_("On what?"), "objects", "all_objects"),
    )
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        widget=ModelSelect2MultipleWidget(
            search_fields=["name__icontains", "short_name__icontains"],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
        required=False,
    )
    persons = forms.ModelMultipleChoiceField(
        queryset=Person.objects.all(),
        widget=ModelSelect2MultipleWidget(
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "short_name__icontains",
            ],
            attrs={"data-minimum-input-length": 0, "class": "browser-default"},
        ),
        required=False,
    )

    objects = forms.ModelMultipleChoiceField(
        queryset=None,
        required=False,
        label=_("Select objects which the permission should be granted for:"),
    )
    all_objects = forms.BooleanField(
        required=False, label=_("Grant the permission for all objects")
    )

    def clean(self) -> dict[str, Any]:
        """Clean form to ensure that at least one target and one type is selected."""
        cleaned_data = super().clean()
        if not cleaned_data.get("persons") and not cleaned_data.get("groups"):
            raise ValidationError(
                _("You must select at least one group or person which should get the permission.")
            )

        if not cleaned_data.get("objects") and not cleaned_data.get("all_objects"):
            raise ValidationError(
                _("You must grant the permission to all objects or to specific objects.")
            )
        return cleaned_data

    def __init__(self, *args, permission: Permission, **kwargs):
        self.permission = permission
        super().__init__(*args, **kwargs)

        model_class = self.permission.content_type.model_class()
        if model_class._meta.managed and not model_class._meta.abstract:
            queryset = model_class.objects.all()
        else:
            # The following queryset is just a dummy one. It has no real meaning.
            # We need it as there are permissions without real objects,
            # but we want to use the same form.
            queryset = Group.objects.none()
        self.fields["objects"].queryset = queryset
        search_fields = getattr(model_class, "get_filter_fields", lambda: [])()

        # Use select2 only if there are any searchable fields as it can't work without
        if search_fields:
            self.fields["objects"].widget = ModelSelect2MultipleWidget(
                search_fields=search_fields,
                queryset=queryset,
                attrs={"data-minimum-input-length": 0, "class": "browser-default"},
            )

    def save_perms(self):
        """Save permissions for selected user/groups and selected/all objects."""
        persons = self.cleaned_data["persons"]
        groups = self.cleaned_data["groups"]
        all_objects = self.cleaned_data["all_objects"]
        objects = self.cleaned_data["objects"]
        permission_name = f"{self.permission.content_type.app_label}.{self.permission.codename}"

        # Create permissions for users
        for person in persons:
            if getattr(person, "user", None):
                # Global permission
                if all_objects:
                    assign_perm(permission_name, person.user)
                # Object permissions
                for instance in objects:
                    assign_perm(permission_name, person.user, instance)

        # Create permissions for users
        for group in groups:
            django_group = group.django_group
            # Global permission
            if all_objects:
                assign_perm(permission_name, django_group)
            # Object permissions
            for instance in objects:
                assign_perm(permission_name, django_group, instance)


class AccountRegisterForm(SignupForm, ExtensibleForm):
    """Form to register new user accounts."""

    class Meta:
        model = Person
        fields = [
            "first_name",
            "additional_name",
            "last_name",
            "addresses",
            "date_of_birth",
            "place_of_birth",
            "sex",
            "photo",
            "mobile_number",
            "phone_number",
            "short_name",
            "description",
        ]

    layout = Layout(
        Fieldset(
            _("Base data"),
            Row("first_name", "additional_name", "last_name"),
            "short_name",
        ),
        Fieldset(
            _("Address data"),
            Row("addresses"),
        ),
        Fieldset(_("Contact data"), Row("mobile_number", "phone_number")),
        Fieldset(
            _("Additional data"),
            Row("date_of_birth", "place_of_birth"),
            Row("sex", "photo"),
            "description",
        ),
        Fieldset(
            _("Account data"),
            "username",
            Row("email", "email2"),
            Row("password1", "password2"),
        ),
    )

    password1 = forms.CharField(label=_("Password"), widget=forms.PasswordInput)

    if settings.SIGNUP_PASSWORD_ENTER_TWICE:
        password2 = forms.CharField(label=_("Password (again)"), widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        request = kwargs.pop("request", None)
        super().__init__(*args, **kwargs)

        person = None
        if request.session.get("account_verified_email"):
            email = request.session["account_verified_email"]

            try:
                person = Person.objects.get(email=email)
            except (Person.DoesNotExist, Person.MultipleObjectsReturned) as exc:
                raise SuspiciousOperation from exc

        elif request.session.get("invitation_code"):
            try:
                invitation = PersonInvitation.objects.get(
                    key=request.session.get("invitation_code")
                )
            except PersonInvitation.DoesNotExist as exc:
                raise SuspiciousOperation from exc

            person = invitation.person

        if person:
            self.instance = person
            available_fields = [field.name for field in Person._meta.get_fields()]
            if person.email:
                self.fields["email"].disabled = True
                self.fields["email2"].disabled = True
                self.fields["email2"].initial = person.email
            for field in self.fields:
                if field in available_fields and getattr(person, field):
                    self.fields[field].disabled = True
                    self.fields[field].initial = getattr(person, field)

    def save(self, request):
        adapter = get_adapter(request)
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)
        # Create person
        data = {}
        for field in Person._meta.get_fields():
            if field.name in self.cleaned_data:
                data[field.name] = self.cleaned_data[field.name]
        if self.instance:
            person_qs = Person.objects.filter(pk=self.instance.pk)
        else:
            person_qs = Person.objects.filter(email=data["email"])
            if not person_qs.exists() and get_site_preferences()["account__auto_create_person"]:
                Person.objects.create(user=user, **data)
        if person_qs.exists():
            person = person_qs.first()
            for field, value in data.items():
                setattr(person, field, value)
            person.user = user
            person.save()
        invitation_code = request.session.get("invitation_code")
        if invitation_code:
            from invitations.views import accept_invitation  # noqa

            try:
                invitation = PersonInvitation.objects.get(key=invitation_code)
            except PersonInvitation.DoesNotExist as exc:
                raise SuspiciousOperation from exc

            accept_invitation(invitation, request, user)
        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user


class ActionForm(forms.Form):
    """Generic form for executing actions on multiple items of a queryset.

    This should be used together with a ``Table`` from django-tables2
    which includes a ``SelectColumn``.

    The queryset can be defined in two different ways:
    You can use ``get_queryset`` or provide ``queryset`` as keyword argument
    at the initialization of this form class.
    If both are declared, it will use the keyword argument.

    Any actions can be defined using the ``actions`` class attribute
    or overriding the method ``get_actions``.
    The actions use the same syntax like the Django Admin actions with one important difference:
    Instead of the related model admin,
    these actions will get the related ``ActionForm`` as first argument.
    Here you can see an example for such an action:

    .. code-block:: python

        from django.utils.translation import gettext as _

        def example_action(form, request, queryset):
            # Do something with this queryset

        example_action.short_description = _("Example action")

    If you can include the ``ActionForm`` like any other form in your views,
    but you must add the request as first argument.
    When the form is valid, you should run ``execute``:

    .. code-block:: python

        from aleksis.core.forms import ActionForm

        def your_view(request, ...):
            # Something
            action_form = ActionForm(request, request.POST or None, ...)
            if request.method == "POST" and form.is_valid():
                form.execute()

            # Something
    """

    layout = Layout("action")
    actions = []

    def get_actions(self) -> Sequence[Callable]:
        """Get all defined actions."""
        return self.actions

    def _get_actions_dict(self) -> dict[str, Callable]:
        """Get all defined actions as dictionary."""
        return {value.__name__: value for value in self.get_actions()}

    def _get_action_choices(self) -> list[tuple[str, str]]:
        """Get all defined actions as Django choices."""
        return [
            (value.__name__, getattr(value, "short_description", value.__name__))
            for value in self.get_actions()
        ]

    def get_queryset(self) -> QuerySet:
        """Get the related queryset."""
        raise NotImplementedError("Queryset necessary.")

    action = forms.ChoiceField(choices=[])
    selected_objects = forms.ModelMultipleChoiceField(queryset=None)

    def __init__(self, request: HttpRequest, *args, queryset: QuerySet = None, **kwargs):
        self.request = request
        self.queryset = queryset if isinstance(queryset, QuerySet) else self.get_queryset()
        super().__init__(*args, **kwargs)
        self.fields["selected_objects"].queryset = self.queryset
        self.fields["action"].choices = self._get_action_choices()

    def clean_action(self):
        action = self._get_actions_dict().get(self.cleaned_data["action"], None)
        if not action:
            raise ValidationError(_("The selected action does not exist."))
        return action

    def clean_selected_objects(self):
        action = self.cleaned_data["action"]
        if hasattr(action, "permission"):
            selected_objects = queryset_rules_filter(
                self.request, self.cleaned_data["selected_objects"], action.permission
            )
            if selected_objects.count() < self.cleaned_data["selected_objects"].count():
                raise ValidationError(
                    _("You do not have permission to run {} on all selected objects.").format(
                        getattr(action, "short_description", action.__name__)
                    )
                )
        return self.cleaned_data["selected_objects"]

    def execute(self) -> Any:
        """Execute the selected action on all selected objects.

        :return: the return value of the action
        """
        if self.is_valid():
            data = self.cleaned_data["selected_objects"]
            action = self.cleaned_data["action"]
            return action(None, self.request, data)

        raise TypeError("execute() must be called on a pre-validated form.")


class ListActionForm(ActionForm):
    """Generic form for executing actions on multiple items of a list of dictionaries.

    Sometimes you want to implement actions for data from different sources
    than querysets or even querysets from multiple models. For these cases,
    you can use this form.

    To provide an unique identification of each item, the dictionaries **must**
    include the attribute ``pk``. This attribute has to be unique for the whole list.
    If you don't mind this aspect, this will cause unexpected behavior.

    Any actions can be defined as described in ``ActionForm``, but, of course,
    the last argument won't be a queryset but a list of dictionaries.

    For further information on usage, you can take a look at ``ActionForm``.
    """

    selected_objects = forms.MultipleChoiceField(choices=[])

    def get_queryset(self):
        # Return None in order not to raise an unwanted exception
        return None

    def _get_dict(self) -> dict[str, dict]:
        """Get the items sorted by pk attribute."""
        return {item["pk"]: item for item in self.items}

    def _get_choices(self) -> list[tuple[str, str]]:
        """Get the items as Django choices."""
        return [(item["pk"], item["pk"]) for item in self.items]

    def _get_real_items(self, items: Sequence[dict]) -> list[dict]:
        """Get the real dictionaries from a list of pks."""
        items_dict = self._get_dict()
        real_items = []
        for item in items:
            if item not in items_dict:
                raise ValidationError(_("No valid selection."))
            real_items.append(items_dict[item])
        return real_items

    def clean_selected_objects(self) -> list[dict]:
        data = self.cleaned_data["selected_objects"]
        items = self._get_real_items(data)
        return items

    def __init__(self, request: HttpRequest, items, *args, **kwargs):
        self.items = items
        super().__init__(request, *args, **kwargs)
        self.fields["selected_objects"].choices = self._get_choices()


class MaintenanceModeForm(forms.Form):
    maintenance_mode = forms.BooleanField(
        required=False,
        initial=not get_maintenance_mode(),
        widget=forms.HiddenInput,
    )
