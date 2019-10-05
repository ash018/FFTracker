from django.contrib import admin
from .models import Message, Thread


class MessageAdmin(admin.ModelAdmin):
    search_fields = (
        'sender__username',
    )
    list_filter = (
        'type',
        'sender',
        'group',
    )

    list_display = (
        'type',
        'sender',
        'text',
        'timestamp',
        'group',
    )


class ThreadAdmin(admin.ModelAdmin):
    search_fields = (
        'name',
    )

    list_filter = (
        'type',
        'org',
    )

    list_display = (
        'name',
        'admin',
        'type',
        'creation_time',
        'member_list',
    )

    def member_list(self, obj):
        members = ''
        for mem in obj.members.all():
            members += mem.full_name + ','
        return members


admin.site.register(Message, MessageAdmin)
admin.site.register(Thread, ThreadAdmin)
