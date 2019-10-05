from django.contrib import admin
from .models import Usage, Subscription, Payment


class SubscriptionAdmin(admin.ModelAdmin):
    search_fields = ['org__oid', ]
    list_filter = (
        'package',
        '_is_trial',
        '_is_premium',
    )

    list_display = (
        'org',
        'current_usage',
        'agent_limit',
        'task_limit',
        'added_agents',
        'currency'
    )


class UsageAdmin(admin.ModelAdmin):
    search_fields = ['org__oid', ]
    list_filter = (
        'status',
    )

    list_display = (
        'org',
        'init_date',
        'exp_date',
        'consumed_tasks',
        'discount',
        'status'
    )


class PaymentAdmin(admin.ModelAdmin):
    search_fields = ['subscription__org__oid', ]
    list_filter = (
        'bill_type',
        'state',
        'gateway',
    )

    list_display = (
        'gateway',
        'vendor_uid',
        'state',
        'amount',
        'bill_type',
        'new_agents',
        'extra_tasks',
        'timestamp',
    )


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(Usage, UsageAdmin)
admin.site.register(Payment, PaymentAdmin)