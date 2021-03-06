"""
MongoEngine models for Social Auth

Requires MongoEngine 0.6.10
"""
try:
    from django.contrib.auth.hashers import UNUSABLE_PASSWORD
    _ = UNUSABLE_PASSWORD  # to quiet flake
except (ImportError, AttributeError):
    UNUSABLE_PASSWORD = '!'

from django.db.models import get_model
from importlib import import_module

from mongoengine import DictField, Document, IntField, ReferenceField, \
                        StringField
from mongoengine.queryset import OperationError

from social_auth.utils import setting
from social_auth.db.base import UserSocialAuthMixin, AssociationMixin, \
                                NonceMixin


USER_MODEL_APP = setting('SOCIAL_AUTH_USER_MODEL') or \
                 setting('AUTH_USER_MODEL')

if USER_MODEL_APP:
    USER_MODEL = get_model(*USER_MODEL_APP.rsplit('.', 1))
else:
    USER_MODEL_MODULE, USER_MODEL_NAME = \
        'mongoengine.django.auth.User'.rsplit('.', 1)
    USER_MODEL = getattr(import_module(USER_MODEL_MODULE), USER_MODEL_NAME)


class UserSocialAuth(Document, UserSocialAuthMixin):
    """Social Auth association model"""
    user = ReferenceField(USER_MODEL, dbref=True)
    provider = StringField(max_length=32)
    uid = StringField(max_length=255, unique_with='provider')
    extra_data = DictField()

    @classmethod
    def get_social_auth_for_user(cls, user):
        return cls.objects(user=user)

    @classmethod
    def create_social_auth(cls, user, uid, provider):
        if not isinstance(type(uid), str):
            uid = str(uid)
        return cls.objects.create(user=user, uid=uid, provider=provider)

    @classmethod
    def username_max_length(cls):
        return UserSocialAuth.user_model().username.max_length

    @classmethod
    def email_max_length(cls):
        return UserSocialAuth.user_model().email.max_length

    @classmethod
    def user_model(cls):
        return USER_MODEL

    @classmethod
    def create_user(cls, *args, **kwargs):
        # Empty string makes email regex validation fail
        if kwargs.get('email') == '':
            kwargs['email'] = None
        kwargs.setdefault('password', UNUSABLE_PASSWORD)
        return cls.user_model().create_user(*args, **kwargs)

    @classmethod
    def allowed_to_disconnect(cls, user, backend_name, association_id=None):
        if association_id is not None:
            qs = cls.objects.filter(id__ne=association_id)
        else:
            qs = cls.objects.filter(provider__ne=backend_name)
        qs = qs.filter(user=user)

        if hasattr(user, 'has_usable_password'):
            valid_password = user.has_usable_password()
        else:
            valid_password = True

        return valid_password or qs.count() > 0


class Nonce(Document, NonceMixin):
    """One use numbers"""
    server_url = StringField(max_length=255)
    timestamp = IntField()
    salt = StringField(max_length=40)


class Association(Document, AssociationMixin):
    """OpenId account association"""
    server_url = StringField(max_length=255)
    handle = StringField(max_length=255)
    secret = StringField(max_length=255)  # Stored base64 encoded
    issued = IntField()
    lifetime = IntField()
    assoc_type = StringField(max_length=64)


def is_integrity_error(exc):
    return exc.__class__ is OperationError and 'E11000' in exc.message
