from rest_framework_jwt import views as jwt
from rest_framework import routers
from django.urls import path

from .auth_apis import PasswordLogin, PasswordChange, PasswordChangeOtp, \
    PasswordSet, Signup, CheckPair, OTPLogin

from apps.user.views import ProfileViewSet, UserAdminViewSet, ResourceViewSet, \
    DataUsageViewSet, DashboardManager, DashboardAgent, ProfileImageUpload, \
    FBTokenUpdateView, FileUpload, SearchAgentsTasks,\
    PaginatedAccounts, PaginatedResources, SearchUsers, ExportAccounts


USER_ULRS = {
    'image_upload_api':  'image/upload/',
    'file_upload_api': 'file/upload/',
    'get_user_api': 'agent/details/',

    'profile': 'profile/',
    'profile_id': 'profile/<int:pk>/',

    'manager_dashboard': 'manager/dashboard/',
    'resource_list': 'manager/resource/',
    'resource_list_paginated': 'manager/resource/paginated/',
    'resource_list_id': 'manager/resource/<int:pk>/',

    'account': 'account/',
    'accounts_paginated': 'account/paginated/',
    'account_id': 'account/<int:pk>/',
    'data_usage': 'data/usage/',
    'data_usage_id': 'data/usage/<int:agent_id>/',

    'agent_phone_activation_api': 'agent/activate/phone/',
    'agent_set_attendance_api': 'agent/set/attendance/',
    'agent_dashboard': 'agent/dashboard/',

    'update_fb_token': 'fbtoken/update/',
    'search_api_manager': 'manager/search/<str:token>/',
    'search_user': 'search/<str:token>/',

    'login_password': 'login/password/',
    'login_otp': 'login/otp/',
    'change_password': 'password/change/',
    'change_password_otp': 'password/change/otp/',
    'set_password': 'password/set/',

    'signup_api': 'signup/',
    'check_pair': 'check/pair/',

    'export_users': 'export/'
}

router = routers.DefaultRouter()
router.register('profile', ProfileViewSet, base_name='manager_profile')
router.register('account', UserAdminViewSet, base_name='manager_agent')
router.register('data/usage', DataUsageViewSet, base_name='usage')
router.register('manager/resource', ResourceViewSet, base_name='manager_resource')


urlpatterns = [
    path('token/refresh/', jwt.refresh_jwt_token),
    path('token/verify/', jwt.verify_jwt_token),
    path('token/get/', jwt.obtain_jwt_token),

    path(USER_ULRS['image_upload_api'], ProfileImageUpload.as_view()),
    path(USER_ULRS['file_upload_api'], FileUpload.as_view()),

    path(USER_ULRS['manager_dashboard'], DashboardManager.as_view()),
    path(USER_ULRS['accounts_paginated'], PaginatedAccounts.as_view()),
    path(USER_ULRS['resource_list_paginated'], PaginatedResources.as_view()),

    path(USER_ULRS['agent_dashboard'], DashboardAgent.as_view()),
    path(USER_ULRS['update_fb_token'], FBTokenUpdateView.as_view()),
    path(USER_ULRS['search_api_manager'], SearchAgentsTasks.as_view()),
    path(USER_ULRS['search_user'], SearchUsers.as_view()),

    path(USER_ULRS['export_users'], ExportAccounts.as_view()),

    path(USER_ULRS['login_password'], PasswordLogin.as_view()),
    path(USER_ULRS['login_otp'], OTPLogin.as_view()),

    path(USER_ULRS['change_password_otp'], PasswordChangeOtp.as_view()),
    path(USER_ULRS['change_password'], PasswordChange.as_view()),
    path(USER_ULRS['set_password'], PasswordSet.as_view()),
    path(USER_ULRS['signup_api'], Signup.as_view()),
    path(USER_ULRS['check_pair'], CheckPair.as_view())

]

urlpatterns += router.urls