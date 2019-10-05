from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from apps.user.serializers import PasswordChangeOTPSerializer, \
    PasswordLoginSerializer, OTPLoginSerializer, SignupSerializer

from apps.user.dict_extractors import *
from apps.user.auth_helpers import *


class Signup(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'oid': 'oid',
                'username': 'username',
                'access_token': 'asdfasdfasdf2',
            }

        Sample Response:
        ---
            {
                'user_details': { profile fields },
                'jwt_token': jwt_token,
            }

        """
        serializer = SignupSerializer(data=request.data)
        if serializer.is_valid():
            user, jwt_token = serializer.signup_user(serializer.validated_data)
            data = {
                'user': get_profile_details(user),
                'jwt_token': jwt_token,
            }
            return Response(data, status=200)
        return Response({'detail': str(serializer.errors)}, status=400)


class PasswordLogin(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'oid': 'oid',
                'username': 'username',
                'password': 'asdfasdfasdf2',
            }

        Sample Response:
        ---
            {
                'user_details': { profile fields },
                'jwt_token': jwt_token,
            }

        """
        serializer = PasswordLoginSerializer(data=request.data)
        if serializer.is_valid():
            user, jwt_token = serializer.authenticate(serializer.validated_data)
            data = {
                'user': get_profile_details(user),
                'jwt_token': jwt_token,
            }
            return Response(data, status=200)
        return Response({'detail': str(serializer.errors)}, status=400)


class OTPLogin(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'oid': 'oid',
                'username': 'username',
                'access_token': 'sfasdfasdfX',
            }

        Sample Response:
        ---
            {
                'user_details': { profile fields },
                'jwt_token': jwt_token,
            }

        """
        serializer = OTPLoginSerializer(data=request.data)
        if serializer.is_valid():
            user, jwt_token = serializer.authenticate(serializer.validated_data)
            data = {
                'user': get_profile_details(user),
                'jwt_token': jwt_token,
            }
            return Response(data, status=200)
        return Response({'detail': str(serializer.errors)}, status=400)


class PasswordChange(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'old_password': 'asdfasdfasdf1',
                'new_password': 'asdfasdfasdf2',
            }
        """
        # print("Request", serializer.data)
        old_password = request.data.get('old_password', False)
        new_password = request.data.get('new_password', False)
        if not (old_password or new_password):
            return Response({'detail': 'Provide old and new password!'}, status=400)

        if len(new_password) < 8:
            return Response({'detail': 'Provide a valid password!'}, status=400)

        user = request.user
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response({'msg': 'OK'}, status=200)
        msg = 'Password do not match'
        return Response({'detail': msg}, status=400)


class PasswordChangeOtp(APIView):
    permission_classes = (AllowAny,)

    def post(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'oid': 'oid',
                'username': 'username',
                'access_token': 'sfasdfasdfX',
                'new_password': 'asdfasdfasdf2',
            }
        """
        serializer = PasswordChangeOTPSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.authenticate(serializer.validated_data)
            data = {
                'msg': 'OK',
            }
            return Response(data, status=200)
        return Response({'detail': str(serializer.errors)}, status=400)


class PasswordSet(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'password': 'asdfasdfasdf1',
            }
        """
        user = request.user
        if user.has_usable_password():
            return Response({'msg': 'Use OTP method!'}, status=406)
        password = request.data.get('password', False)
        if not password or len(password) < 8:
            return Response({'msg': 'Provide a valid password!'}, status=400)

        user.set_password(password)
        user.save()
        return Response({'msg': 'OK'}, status=200)


class CheckPair(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                'oid': 'oid',
                'username': 'username',
            }
        """
        oid = request.query_params.get('oid', False)
        oid = oid.lower()
        username = request.query_params.get('username', False)

        if not (oid and username):
            return Response({'detail': 'Provide username and OID!'}, status=400)

        if check_oid_exists(oid):
            return Response({'detail': 'Organization exists!'}, status=400)
        if check_username_exists(oid=oid, username=username):
            return Response({'detail': 'Username exists!'}, status=400)

        return Response({'msg': 'OK'}, status=200)
