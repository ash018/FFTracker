from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from rest_framework.response import Response
from apps.user.permissions import is_manager
from apps.message.models import Message
from .config import MSG_DICT as MSGD
from .models import Thread
from .helpers import *
from apps.message.config import send_msg_payload, send_group_message
from apps.user.models import User
from apps.common.helpers import get_paginated
from apps.user.dict_extractors import get_user_list


class NewThread(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Parameter details:
        ---
            text:
                type: str
                required: No
            recipient_id:
                type: int
                required: yes
            attachments:
                type: json list
                example: ['url1', 'url2']
            timestamp:
                type: datetime
                required: No
        """

        sender = request.user
        recipient_id = request.data.get('recipient_id', False)
        if not recipient_id:
            return Response({'message': 'No recipient found!'}, status=406)
        recipient = User.objects.select_related(
            'org'
        ).get(id=recipient_id)
        private_name1 = 'Private_' + str(sender.id) + '_' + str(recipient.id) + '_' + sender.org.oid
        private_name2 = 'Private_' + str(recipient.id) + '_' + str(sender.id) + '_' + sender.org.oid
        if sender.org != recipient.org:
            return Response({'message': 'Messaging outside team not allowed!'}, status=406)

        qmsg_group = Q(name=private_name1) | Q(name=private_name2)

        message_time = timezone.now()

        thread_qs = Thread.objects.filter(qmsg_group)
        if len(thread_qs) > 0:
            p2p_group = thread_qs[0]
            p2p_group.last_message_time = message_time
            p2p_group.save()
        else:
            p2p_group = Thread.objects.create(org=sender.org)
            p2p_group.members.add(sender, recipient)
            p2p_group.name = private_name1
            p2p_group.last_message_time = message_time
            # Null admin for 'Private' group
            p2p_group.save()
        text = request.data.get('text', ' ')
        attachments = request.data.get('attachments')
        # TODO: set timestamp
        message = Message.objects.create(
            text=text,
            attachments=attachments,
            sender=sender,
            timestamp=message_time,
            group=p2p_group
        )
        resp = send_msg_payload(message, recipient)
        # print(resp)
        data = {
            'thread_id': p2p_group.id,
            'fb_resp': resp
        }
        return Response(data, status=200)


class OldThread(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Parameter details:
        ---
            text:
                type: str
                required: No
            thread_id:
                type: int
                required: yes
            attachments:
                type: json list
                example: ['url1', 'url2']
            timestamp:
                type: datetime
                required: No
        """

        sender = request.user
        thread_id = request.data.get('thread_id', False)
        message_time = timezone.now()
        if not thread_id:
            return Response({'message': 'No Thread found!'}, status=406)
        text = request.data.get('text', ' ')
        attachments = request.data.get('attachments')

        chat_group = Thread.objects.get(id=thread_id)
        chat_group.last_message_time = message_time
        chat_group.save()
        message = Message(
            text=text,
            attachments=attachments,
            sender=sender,
            timestamp=message_time,
            group=chat_group
        )
        if chat_group.admin:
            message.type = MSGD['Group']
        message.save()
        resp = send_group_message(message, chat_group)
        # print(resp)
        return Response(resp, status=200)


class Conversations(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            msg_type:
                type: str
                required: No
        """

        user = request.user
        qcommon_grp = Q(members=user)
        groups = Thread.objects.filter(qcommon_grp).order_by('-last_message_time').distinct()
        conversations = []
        for grp in groups:
            message = Message.objects.select_related(
                'sender', 'group'
            ).filter(group=grp).order_by('-timestamp')[0]
            conversations.append(get_thread_content(message, user))

        return Response(conversations, status=200)


class Messages(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, thread_id, format=None):
        """
        Parameter details:
        ---
            thread_id:
                type: int
                required: Yes
        """
        if not Thread.objects.filter(id=thread_id):
            return Response({'message': 'No Thread found!'}, status=400)
        message_qs = Message.objects.filter(group_id=thread_id).order_by('-timestamp')
        message_list = []
        for msg in message_qs:
            message_list.append(get_message_content(msg))

        return Response(message_list, status=200)


class PaginatedMessages(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, thread_id, format=None):
        """
        Parameter details:
        ---
            thread_id:
                type: int
                required: Yes
        """
        if not Thread.objects.filter(id=thread_id):
            return Response({'message': 'No Thread found!'}, status=400)
        message_qs = Message.objects.filter(
            group_id=thread_id
        ).order_by('-timestamp')
        data = get_paginated(
            message_qs,
            request,
            get_message_list
        )

        return Response(data, status=200)


class ChatGroup(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Parameter details:
        ---
            group_name:
                type: str
                required: No
            member_list:
                type: json list
                example: [id1, id2,...]
        """
        is_manager(request)
        manager = request.user
        group_name = request.data.get('group_name', manager.full_name + '_' + get_rand_str(8))
        member_list = request.data.get('member_list', False)
        if not member_list:
            return Response({'message': 'No member provided!'}, status=406)
        # print(member_list)
        chat_group = Thread(
            name=group_name,
            admin=manager,
            org=manager.org,
            type=MSGD['Group']
        )
        chat_group.save()
        chat_group.members.add(manager)
        for mem_id in member_list:
            chat_group.members.add(User.objects.get(id=mem_id))
        chat_group.save()
        text = 'You joined the group ' + group_name + ' created by ' + manager.full_name
        # TODO: set timestamp
        message = Message.objects.create(
            text=text,
            sender=manager,
            type=MSGD['Group'],
            timestamp=timezone.now(),
            group=chat_group
        )
        resp = send_group_message(message, chat_group)
        return Response(resp, status=201)


class EditChatGroup(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request, pk, format=None):
        """
        Parameter details:
        ---
            group_name:
                type: str
                required: No
            member_list:
                type: json list
                example: [id1, id2,...]
        """
        is_manager(request)
        admin = request.user
        chat_group = Thread.objects.get(id=pk)
        group_name = request.data.get('group_name', False)
        member_list = request.data.get('member_list', False)
        if member_list:
            chat_group.members.clear()
            chat_group.members.add(admin)
            for mem_id in member_list:
                chat_group.members.add(User.objects.get(id=mem_id))
        if group_name:
            chat_group.name = group_name

        chat_group.save()
        text = 'Group ' + group_name + ' has been modified by ' + admin.full_name
        # TODO: set timestamp
        message = Message.objects.create(
            text=text,
            sender=admin,
            type=MSGD['Group'],
            timestamp=timezone.now(),
            group=chat_group
        )
        resp = send_group_message(message, chat_group)
        return Response(resp, status=200)


class FriendList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Sample Response:
        ---

            [
                {
                    'id': 222,
                    'username': 'username1',
                    'full_name': 'full_name',
                    'image': 'image_url..',
                    'designation': 'designation',
                    'phone': 'phone',
                    'manager_name': 'manager_name',
                    'manager_id': 23,
                    'manager_image': 'image_url..',
                    'manager_designation': 'designation',
                    'role': 1,
                },..
            ]


        """
        viewer = request.user
        users_qf = Q(parent=viewer)
        if viewer.parent:
            users_qf |= Q(id=viewer.parent.id)
        users_qs = User.objects.filter(users_qf)
        user_list = get_user_list(users_qs)

        return Response(user_list, status=200)


