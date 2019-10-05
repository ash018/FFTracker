from django.urls import path
from rest_framework import routers
from apps.billing.views import GetAppUsage, BkashPaymentTemplate, \
    CreatePaymentBkash, ExecutePaymentBkash, BkashPaymentErrorPage, \
    BkashPaymentSuccessPage, NewSubscriptionBill, \
    ExtraTasksBill, NewAgentsBill, ExecutePaymentSSL, SendMail, \
    PackageViewSet, ssl_redirect, CreatePaymentSSL, CreatePaymentInternal
from .config import BILL_URLS


router = routers.DefaultRouter()
router.register('manager/premium', PackageViewSet, base_name='manager_premium')

urlpatterns = [
    path(BILL_URLS['get_usage'], GetAppUsage.as_view()),
    path(BILL_URLS['payment_create_internal'], CreatePaymentInternal.as_view()),
    path(BILL_URLS['bkash_template'], BkashPaymentTemplate.as_view()),
    path(BILL_URLS['bkash_success_template'], BkashPaymentSuccessPage.as_view()),
    path(BILL_URLS['bkash_fail_template'], BkashPaymentErrorPage.as_view()),
    path(BILL_URLS['create_payment'], CreatePaymentBkash.as_view()),
    path(BILL_URLS['execute_payment'], ExecutePaymentBkash.as_view()),
    path(BILL_URLS['new_subscription_bill'], NewSubscriptionBill.as_view()),
    path(BILL_URLS['extra_tasks_bill'], ExtraTasksBill.as_view()),
    path(BILL_URLS['new_agents_bill'], NewAgentsBill.as_view()),

    path(BILL_URLS['ssl_redirect'], ssl_redirect),
    path(BILL_URLS['ssl_create'], CreatePaymentSSL.as_view()),
    path(BILL_URLS['execute_payment_ssl'], ExecutePaymentSSL.as_view()),
    path(BILL_URLS['send_mail'], SendMail.as_view()),
]

urlpatterns += router.urls
