# from rest_framework_jwt import views as jwt
from django.urls import path
from apps.message.views import NewThread, OldThread, \
    Conversations, Messages, ChatGroup, EditChatGroup, \
    FriendList, PaginatedMessages


MSG_ULRS = {
    'message_old_thread':  'old/',
    'user_list': 'users/',
    'message_new_thread':  'new/',
    'get_conversations':  'conversations/',
    'get_messages':  '<int:thread_id>/',
    'get_messages_paginated': 'paginated/<int:thread_id>/',
    'create_chat_group': 'group/',
    'edit_chat_group': 'group/<int:pk>/',

}

urlpatterns = [
    path(MSG_ULRS['message_new_thread'], NewThread.as_view()),
    path(MSG_ULRS['message_old_thread'], OldThread.as_view()),
    path(MSG_ULRS['get_conversations'], Conversations.as_view()),
    path(MSG_ULRS['get_messages'], Messages.as_view()),
    path(MSG_ULRS['get_messages_paginated'], PaginatedMessages.as_view()),
    path(MSG_ULRS['create_chat_group'], ChatGroup.as_view()),
    path(MSG_ULRS['edit_chat_group'], EditChatGroup.as_view()),
    path(MSG_ULRS['user_list'], FriendList.as_view()),
]