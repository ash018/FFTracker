from django.contrib import admin
from .models import Location, ClientLocation


class LocationAdmin(admin.ModelAdmin):
    search_fields = ['agent__username', 'address']
    list_filter = (
        'org',
        'event',
    )

    list_display = (
        'agent',
        'org',
        'timestamp',
        'address',
        'event',
    )


class ClientLocationAdmin(admin.ModelAdmin):
    search_fields = ['name', ]
    list_filter = (
        'org',
        'name'
    )

    list_display = (
        'name',
        'address',
        'point',
        'org',
    )


admin.site.register(Location, LocationAdmin)
admin.site.register(ClientLocation, ClientLocationAdmin)