from django.contrib import admin
from .models import Lead


class LeadAdmin(admin.ModelAdmin):
    list_filter = (
        'company_name',
        'employee_count'
    )

    list_display = (
        'name',
        'phone',
        'email',
        'company_name',
        'domain_choice',
        'employee_count',

    )


admin.site.register(Lead, LeadAdmin)
