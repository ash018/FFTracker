import requests
from rest_framework.exceptions import NotAcceptable
from apps.user.models import User
from apps.user.config import ROLE_DICT

FB_AUTH_URL = 'https://graph.accountkit.com/v1.1/me?access_token='


def set_active(user):
    if not user.is_active:
        user.is_active = True
        user.save()


def get_phone(access_token):
    try:
        resp = requests.get(FB_AUTH_URL + access_token).json()
        # print(str(resp))
        phone = resp['phone']['number']
        return phone
    except Exception as e:
        raise NotAcceptable(detail='Error in FB auth token!')


class FBAuthKit:
    name = "accountkit-phone"

    def authenticate_organizer(self, access_token, *args, **kwargs):
        try:
            resp = requests.get(FB_AUTH_URL + access_token).json()
            phone = resp['phone']['number']
            user, created = User.objects.get_or_create(phone=phone)
            if created:
                user.phone = phone
                user.set_unusable_password()
                user.is_active = True
                user.role = ROLE_DICT['Organizer']
                user.save()
            return user
        except Exception as e:
            return None

    def authenticate_manager(self, access_token, *args, **kwargs):
        try:
            resp = requests.get(FB_AUTH_URL + access_token).json()
            phone = resp['phone']['number']
            user = User.objects.get(username=phone)
            if user.role not in [ROLE_DICT['Manager'], ROLE_DICT['Organizer']]:
                return None
            set_active(user)
            return user
        except Exception as e:
            return None

    def authenticate_agent(self, access_token, *args, **kwargs):
        try:
            resp = requests.get(FB_AUTH_URL + access_token).json()
            # print(str(resp))
            phone = resp['phone']['number']
            user = User.objects.get(username=phone)
            if user.role != ROLE_DICT['Employee']:
                return None
            set_active(user)
            return user
        except Exception as e:
            return None

    def change_password(self, access_token, password, *args, **kwargs):
        try:
            resp = requests.get(FB_AUTH_URL + access_token).json()
            # print(str(resp))
            phone = resp['phone']['number']
            user = User.objects.get(username=phone)
            # print(user, password)
            user.set_password(password)
            user.save()
            return user
        except Exception as e:
            return None
