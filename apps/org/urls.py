from django.urls import path
from rest_framework import routers
from apps.org.views import UserExcelUpload, OrganizationViewSet, \
    ClientLocationViewSet, TaskExcelUpload, \
    LocationExcelUpload, DeleteAccount, OrgUrl, UserCSVUpload, TaskCSVUpload, LocationCSVUpload


ORG_URLS = {
    'org_org':  'org/',
    'get_tasks_org_paginated': 'task/paginated/',
    'org_org_id':  'org/<int:pk>/',

    'upload_users':  'upload/users/',
    'upload_users_csv': 'upload/users/csv/',
    'upload_tasks':  'upload/tasks/',
    'upload_tasks_csv':  'upload/tasks/csv/',
    'upload_locations': 'upload/locations/',
    'upload_locations_csv': 'upload/locations/csv/',

    'org_task': 'task/',
    'org_task_id': 'task/<int:pk>/',

    'org_client_location': 'client/location/',
    'org_client_location_id': 'client/location/<int:pk>/',

    'org_organizer': 'organizer/',
    'org_organizer_id': 'organizer/<int:pk>/',
    'org_delete': 'delete/'

}

router = routers.DefaultRouter()
router.register('org', OrganizationViewSet, base_name='org_org')
router.register('client/location', ClientLocationViewSet, base_name='org_client_location')

urlpatterns = [
    path(ORG_URLS['upload_users'], UserExcelUpload.as_view()),
    path(ORG_URLS['upload_users_csv'], UserCSVUpload.as_view()),
    path(ORG_URLS['upload_tasks'], TaskExcelUpload.as_view()),
    path(ORG_URLS['upload_tasks_csv'], TaskCSVUpload.as_view()),
    path(ORG_URLS['upload_locations'], LocationExcelUpload.as_view()),
    path(ORG_URLS['upload_locations_csv'], LocationCSVUpload.as_view()),
    path(ORG_URLS['org_delete'], DeleteAccount.as_view()),
    path('oid/<str:url>/', OrgUrl.as_view())
]

urlpatterns += router.urls
