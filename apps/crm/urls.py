from django.urls import path

from .views import LeadSignupPage, LeadSignupApi, SuccessPage
from .helpers import CRM_URLS


urlpatterns = [
    path(CRM_URLS['signup_page'], LeadSignupPage.as_view()),
    path(CRM_URLS['signup_api'], LeadSignupApi.as_view()),
    path(CRM_URLS['success_page'], SuccessPage.as_view()),
]