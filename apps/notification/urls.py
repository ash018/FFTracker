from django.urls import path
from apps.notification.views import Notifications, \
    SOSCreate, GetCount, SetCount, PaginatedNotifications, MarkAllRead


NTF_ULRS = {
    'get_notifications':  'all/',
    'get_notifications_paginated': 'paginated/',
    'get_count':  'count/',
    'set_count':  'checked/<int:pk>/',
    'mark_all_read':  'allread/',
    'create_notifications':  'create/',

}

urlpatterns = [
    path(NTF_ULRS['get_notifications'], Notifications.as_view()),
    path(NTF_ULRS['get_notifications_paginated'], PaginatedNotifications.as_view()),
    path(NTF_ULRS['create_notifications'], SOSCreate.as_view()),
    path(NTF_ULRS['get_count'], GetCount.as_view()),
    path(NTF_ULRS['set_count'], SetCount.as_view()),
    path(NTF_ULRS['mark_all_read'], MarkAllRead.as_view()),
]
