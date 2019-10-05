from rest_framework.permissions import BasePermission
from rest_framework.exceptions import NotAcceptable, PermissionDenied
from .config import ROLE_DICT
from apps.user.models import User
from apps.task.config import TASK_STATUS_DICT as TSD


def role_agent(request):
    return request.user.role == ROLE_DICT['Employee']


def can_message(user1, user2):
    if not (user1.parent == user2 or user2.parent == user1):
        raise PermissionDenied(detail='Permission denied!')


def role_organizer(request):
    return request.user.role == ROLE_DICT['Organizer']


def role_manager(request):
    return request.user.role in [ROLE_DICT['Manager'], ROLE_DICT['Organizer']]


def is_manager(request):
    if not (request.user and role_manager(request)):
        raise PermissionDenied(detail='Permission denied!')


def is_agent(request):
    if not (request.user and role_agent(request)):
        raise PermissionDenied(detail='Permission denied!')


def is_organizer(request):
    if not (request.user and role_organizer(request)):
        raise PermissionDenied(detail='Permission denied!')


class CanUpdateTask(BasePermission):
    def has_object_permission(self, request, view, task):
        if not request.user:
            return False
        user = request.user
        manager = task.manager

        if manager.org != user.org:
            return False

        if user.role in [ROLE_DICT['Organizer'], ROLE_DICT['Manager']]:
            return True
        return False


class IsAgentOfTask(BasePermission):
    def has_object_permission(self, request, view, task):
        if not request.user:
            return False
        agent = request.user
        if agent in task.agent_list.all():
            return True
        if task.manager == agent.parent and task.status == TSD['Unassigned']:
            return True
        return False

