from django.urls import path
from rest_framework import routers
from apps.task.views import AddressFromPoint, \
    ChangeTaskManager, TaskViewSetManager, \
    TaskViewSetAgent, SelfAssignTask, TaskTemplateViewSet, \
    PaginatedTasks, ExportTasks


TASK_URLS = {
    'get_task_list_manager': 'manager/',
    'get_task_list_paginated': 'paginated/',
    'get_task_manager': 'manager/<int:pk>/',
    'create_task_manager': 'manager/',
    'edit_task_manager': 'manager/<int:pk>/',
    'change_task_state_manager': 'manager/state/<int:pk>/',
    'get_task_agent': 'agent/<int:pk>/',
    'create_task_agent': 'agent/',
    'get_task_list_agent': 'agent/',
    'assign_task_agent': 'agent/assign/<int:pk>/',

    'change_task_state_agent': 'agent/<int:pk>/',
    'get_address_from_point': 'address/',

    'get_template': 'template/<int:pk>/',
    'get_templates': 'template/',
    'create_template': 'template/',
    'edit_template': 'template/<int:pk>/',
    'delete_template': 'template/<int:pk>/',

    'export_tasks': 'export/',

}

router = routers.DefaultRouter()
router.register('manager', TaskViewSetManager, base_name='task_manager')
router.register('agent', TaskViewSetAgent, base_name='task_agent')
router.register('template', TaskTemplateViewSet, base_name='task_template')


urlpatterns = [
    path(TASK_URLS['change_task_state_manager'], ChangeTaskManager.as_view()),
    path(TASK_URLS['get_task_list_paginated'], PaginatedTasks.as_view()),
    path(TASK_URLS['get_address_from_point'], AddressFromPoint.as_view()),
    path(TASK_URLS['assign_task_agent'], SelfAssignTask.as_view()),
    path(TASK_URLS['export_tasks'], ExportTasks.as_view()),
    # path('delete/<int:pk>', GetUserView.as_view()),
]

urlpatterns += router.urls