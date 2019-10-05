from rest_framework.serializers import ModelSerializer
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from rest_framework import serializers
from mptt.exceptions import InvalidMove
from django.core.validators import RegexValidator

from apps.user.auth_helpers import *

from apps.user.models import User
from apps.state.models import UserState
from apps.billing.models import Subscription, Usage
from apps.billing.helpers import adjust_user_count
from apps.org.serializers import trial_cycle
from apps.user.fb_auth import get_phone
from apps.org.models import Organization
from .config import ROLE_DICT


alphanumeric = RegexValidator(r'^[0-9a-zA-Z]*$', 'Only alphanumeric characters are allowed.')


class AccountSerializerEmployee(ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username',
            'full_name',
            'designation',
            'phone',
            'email',
            'domain',
        ]

    def update_user(self, user, validated_data):
        oid = user.org.oid
        user_handle = validated_data.get('username', None)
        if user_handle:
            if not user_handle.isalnum():
                raise ValidationError(detail='Only alphanumeric characters are allowed!')
            # print(user.username, user_handle)
            username = create_username(oid, user_handle)
            if user.username != username and check_username_exists(oid, user_handle):
                raise NotAcceptable(detail='username exists!')
            validated_data['username'] = username

        try:
            user = self.update(user, validated_data)
        except Exception as e:
            print(str(e))
            raise NotAcceptable(detail='Something went wrong!')
        return user


class AccountSerializerAdmin(ModelSerializer):

    class Meta:
        model = User
        fields = [
            'username',
            'full_name',
            'designation',
            'phone',
            'email',
            'parent',
            'role',
        ]

        extra_kwargs = {
            'username': {'validators': []},
        }
    
    def create_user(self, validated_data, request):
        org = request.user.org
        user_handle = validated_data['username']
        if not user_handle.isalnum():
            raise NotAcceptable(detail='Only alphanumeric characters are allowed!')
        if check_username_exists(org.oid, user_handle):
            raise NotAcceptable(detail='username exists!')
        validated_data['username'] = create_username(org.oid, user_handle)
        user = self.create(validated_data)
        # TODO: adjust account counter
        user.is_active = True
        user.org = org
        userstate = UserState.objects.create(
            user=user
        )
        user.set_unusable_password()
        user.save()
        adjust_user_count(request)
        return user

    def update_user(self, user, validated_data):
        oid = user.org.oid
        user_handle = validated_data['username']
        if not user_handle.isalnum():
            raise ValidationError(detail='Only alphanumeric characters are allowed!')
        # print(user.username, user_handle)
        username = create_username(oid, user_handle)
        if user.username != username and check_username_exists(oid, user_handle):
            raise NotAcceptable(detail='username exists!')
        validated_data['username'] = username

        parent = validated_data['parent']
        if parent:
            if user.parent != parent:
                try:
                    user.move_to(target=parent, position='last-child')
                except InvalidMove as e:
                    print(str(e))
                    raise NotAcceptable(detail='Invalid manager assignment!')
                except Exception as e:
                    print(str(e))
                    raise NotAcceptable(detail='Something went wrong!')
        else:
            user.move_to(target=None, position='last-child')
        validated_data.pop('parent')

        try:
            user = self.update(user, validated_data)
        except Exception as e:
            print(str(e))
            raise NotAcceptable(detail='Something went wrong!')
        return user


class PasswordLoginSerializer(serializers.Serializer):
    oid = serializers.CharField(max_length=64, required=True)
    username = serializers.CharField(max_length=32, required=True)
    password = serializers.CharField(max_length=255, required=True)

    def authenticate(self, validated_data):
        oid = validated_data['oid']
        oid = oid.lower()
        username = validated_data['username']
        password = validated_data['password']

        user = check_pair(oid=oid, username=username)
        if not user.check_password(password):
            raise AuthenticationFailed(detail='Invalid credentials!')
        
        jwt_token = jwt_encode_handler(jwt_payload_handler(user))
        return user, jwt_token


class OTPLoginSerializer(serializers.Serializer):
    oid = serializers.CharField(max_length=64, required=True)
    username = serializers.CharField(max_length=32, required=True)
    access_token = serializers.CharField(max_length=255, required=True)

    def authenticate(self, validated_data):
        oid = validated_data['oid']
        oid = oid.lower()
        username = validated_data['username']
        access_token = validated_data['access_token']
        phone = get_phone(access_token)

        user = check_pair(oid=oid, username=username)
        if user.phone != phone:
            raise AuthenticationFailed(detail='Invalid Phone!')
        
        jwt_token = jwt_encode_handler(jwt_payload_handler(user))
        return user, jwt_token


class PasswordChangeOTPSerializer(serializers.Serializer):
    oid = serializers.CharField(max_length=64, required=True)
    username = serializers.CharField(max_length=32, required=True)
    access_token = serializers.CharField(max_length=255, required=True)
    new_password = serializers.CharField(max_length=64, required=True)

    def authenticate(self, validated_data):
        oid = validated_data['oid']
        oid = oid.lower()
        username = validated_data['username']
        access_token = validated_data['access_token']
        phone = get_phone(access_token)

        user = check_pair(oid=oid, username=username)
        if user.phone != phone:
            raise PermissionDenied(detail='Invalid Phone!')

        if len(validated_data['new_password']) < 8:
            raise ValidationError(detail='At least !')

        user.set_password(validated_data['new_password'])
        user.save()
        return user


class SignupSerializer(serializers.Serializer):
    oid = serializers.CharField(max_length=64, required=True, validators=[alphanumeric])
    username = serializers.CharField(max_length=32, required=True, validators=[alphanumeric])
    access_token = serializers.CharField(max_length=255, required=True)

    def signup_user(self, validated_data):
        oid = validated_data['oid']
        oid = oid.lower()
        username = validated_data['username']
        access_token = validated_data['access_token']
        try:
            phone = get_phone(access_token)
        except Exception as e:
            raise ValidationError(detail='Invalid phone token!')

        if check_oid_exists(oid):
            raise PermissionDenied(detail='Organization exists!')
        if check_username_exists(oid=oid, username=username):
            raise PermissionDenied(detail='Username exists!')

        org = Organization.objects.create(oid=oid)
        usage = Usage(org=org, exp_date=trial_cycle())
        usage.save()
        subscription = Subscription(org=org, current_usage=usage, _is_trial=True)
        subscription.save()

        user = User(
            username=create_username(oid=oid, username=username),
            phone=phone,
            is_active=True,
            role=ROLE_DICT['Organizer'],
            org=org,
        )
        user.set_unusable_password()
        user.save()
        userstate = UserState.objects.create(
            user=user
        )
        jwt_token = jwt_encode_handler(jwt_payload_handler(user))
        return user, jwt_token
