from django.urls import path
from rest_framework import routers
from apps.assignment.views import AssignmentViewSet, AddComment, \
    PaginatedAssignments, UpdateProgress


ASSIGNMENT_URLS = {
    'assignment': 'object/',
    'assignment_id': 'object/<int:pk>/',
    'assignments_paginated': 'object/paginated/',

    'assignment_progress': 'progress/<int:pk>/',

    'comment': 'comment/',

}

router = routers.DefaultRouter()
router.register('object', AssignmentViewSet, base_name='assignment_object')


urlpatterns = [
    path(ASSIGNMENT_URLS['comment'], AddComment.as_view()),
    path(ASSIGNMENT_URLS['assignment_progress'], UpdateProgress.as_view()),
    path(ASSIGNMENT_URLS['assignments_paginated'], PaginatedAssignments.as_view()),
]

urlpatterns += router.urls
