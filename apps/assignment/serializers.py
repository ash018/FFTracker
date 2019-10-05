from rest_framework.serializers import ModelSerializer, Serializer
# from rest_framework import serializers
from apps.user.config import ROLE_DICT
from rest_framework.exceptions import NotAcceptable, ValidationError, PermissionDenied

from .models import Assignment, Comment
from apps.notification.config import NOTIFICATION_DICT as NTD
from apps.notification.transmitters import assignment_notification


class AssignmentSerializer(ModelSerializer):

    class Meta:
        model = Assignment
        fields = [
            'title',
            'description',
            'org',
            'deadline',
            'status',

            'manager',
            'assignee',
            'assignee_list',
            'custom_fields',
        ]

    def create_assignment(self, validated_data, request):
        user = request.user
        assignment = self.create(validated_data)
        actor_list = [assignment.manager, assignment.assignee]
        for user in assignment.assignee_list.all():
            actor_list.append(user)
        if user not in actor_list:
            assignment.creator = user
            assignment.save()

        text = user.full_name + ' just created assignment: ' + assignment.title
        assignment_notification(assignment, NTD['Assignment Created'], user, text)
        return assignment

    def update_assignment(self, assignment, validated_data, request):
        user = request.user
        valid_role = ROLE_DICT['Organizer']
        valid_list = [assignment.manager, assignment.assignee, assignment.creator]
        if user not in valid_list and user.role != valid_role:
            raise PermissionDenied(detail='Permission Denied!')

        assignment = self.update(assignment, validated_data)
        text = user.full_name + ' just modified assignment: ' + assignment.title
        assignment_notification(assignment, NTD['Assignment Modified'], user, text)
        return assignment


class CommentSerializer(ModelSerializer):

    class Meta:
        model = Comment
        fields = [
            'text',
            'attachments',
            'user',
            'assignment',
        ]


