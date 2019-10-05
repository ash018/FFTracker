from django.contrib import admin
from .models import CustomerSupport


class CustomerSupportAdmin(admin.ModelAdmin):
    list_filter = (
        'org',
        'status',
        'date_created'
    )

    list_display = (
        'subject',
        'user',
        'org',
        'status',
        'date_created'
    )


admin.site.register(CustomerSupport, CustomerSupportAdmin)
