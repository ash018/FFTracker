from apps.user.models import User
from apps.org.models import Organization
from rest_framework.exceptions import NotAcceptable, PermissionDenied, \
    AuthenticationFailed, ValidationError

SPLITTER = '<@/>'


def check_same_org(user, viewer):
    if user.org != viewer.org:
        raise PermissionDenied(detail='User not in your org!')


def check_username_exists(oid, username):
    username = oid + SPLITTER + username
    return User.objects.filter(username=username).exists()


def create_username(oid, username):
    username = oid + SPLITTER + username
    return username


def get_user(oid, username):
    if check_username_exists(oid, username):
        user = User.objects.get(username=oid + SPLITTER + username)
        return user
    return None


def get_username(user):
    username = str(user.username)
    return username.split(SPLITTER)[1]


def set_username(user, username):
    try:
        user.username = create_username(user.org.oid, username)
        user.save()
        return True
    except Exception as e:
        return False


def check_oid_exists(oid):
    return Organization.objects.filter(oid=oid).exists()


def check_pair(oid, username):
    if not check_oid_exists(oid):
        raise AuthenticationFailed(detail='Invalid OID!')
    if not check_username_exists(oid=oid, username=username):
        raise AuthenticationFailed(detail='Invalid Username!')
    return get_user(oid, username)