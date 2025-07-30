import graphene
from graphene_django import DjangoObjectType

from aleksis.core.models import OAuthAccessToken, OAuthApplication

from .base import (
    BaseBatchCreateMutation,
    BaseBatchDeleteMutation,
    BaseBatchPatchMutation,
    FieldFileType,
    PermissionsTypeMixin,
)


class OAuthScopeType(graphene.ObjectType):
    name = graphene.String()
    description = graphene.String()


class OAuthApplicationType(PermissionsTypeMixin, DjangoObjectType):
    class Meta:
        model = OAuthApplication
        fields = [
            "id",
            "name",
            "icon",
            "client_id",
            "client_secret",
            "client_type",
            "algorithm",
            "allowed_scopes",
            "redirect_uris",
            "skip_authorization",
        ]

    icon = graphene.Field(FieldFileType)

    @staticmethod
    def resolve_algorithm(root, info, **kwargs):
        """graphene-django-cud has the undocumented behavior to use "A_" instead of the empty
        string"""
        if not root.algorithm:
            return "A_"
        else:
            return root.algorithm

    @staticmethod
    def resolve_client_secret(root, info, **kwargs):
        """Always return empty client secret as hashed client secret is no useful information."""
        return ""


class InitOAuthApplicationType(graphene.ObjectType):
    client_id = graphene.String()
    client_secret = graphene.String()


class OAuthAccessTokenType(DjangoObjectType):
    scopes = graphene.List(OAuthScopeType)

    @staticmethod
    def resolve_scopes(root: OAuthAccessToken, info, **kwargs):
        return [OAuthScopeType(name=key, description=value) for key, value in root.scopes.items()]

    class Meta:
        model = OAuthAccessToken
        fields = ["id", "application", "expires", "created", "updated"]


class OAuthBatchRevokeTokenMutation(graphene.Mutation):
    class Arguments:
        ids = graphene.List(graphene.ID)

    ok = graphene.Boolean()

    @staticmethod
    def mutate(root, info, ids):
        OAuthAccessToken.objects.filters(pk__in=ids, user=info.context.user).delete()
        return len(ids)


class OAuthApplicationBatchCreateMutation(BaseBatchCreateMutation):
    class Meta:
        model = OAuthApplication
        permissions = ("core.create_oauthapplication_rule",)
        only_fields = (
            "name",
            "icon",
            "client_id",
            "client_secret",
            "client_type",
            "algorithm",
            "allowed_scopes",
            "redirect_uris",
            "skip_authorization",
        )


class OAuthApplicationBatchDeleteMutation(BaseBatchDeleteMutation):
    class Meta:
        model = OAuthApplication
        permissions = ("core.delete_oauthapplication_rule",)


class OAuthApplicationBatchPatchMutation(BaseBatchPatchMutation):
    class Meta:
        model = OAuthApplication
        permissions = ("core.edit_oauthapplication_rule",)
        only_fields = (
            "id",
            "name",
            "icon",
            "client_type",
            "algorithm",
            "allowed_scopes",
            "redirect_uris",
            "skip_authorization",
        )
