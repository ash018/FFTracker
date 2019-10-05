from django.urls import path
from rest_framework import routers

from apps.support.views import CustomerSupportViewSet


SUPPORT_ULRS = {
    'support':  '',
    'support_id':  '<int:pk>/',

}

router = routers.DefaultRouter()
router.register('user', CustomerSupportViewSet, base_name='support_user')

urlpatterns = [

]

urlpatterns += router.urls