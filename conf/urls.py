from django.contrib import admin
from rest_framework_swagger.views import get_swagger_view
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('apidoc/', get_swagger_view(title='Teamwork API Documentation')),
    path('v0/user/', include('apps.user.urls')),
    path('v0/org/', include('apps.org.urls')),
    path('v0/task/', include('apps.task.urls')),
    path('v0/location/', include('apps.location.urls')),
    path('v0/message/', include('apps.message.urls')),
    path('v0/notification/', include('apps.notification.urls')),
    path('v0/billing/', include('apps.billing.urls')),
    path('v0/report/', include('apps.report.urls')),
    path('v0/support/', include('apps.support.urls')),
    path('v0/crm/', include('apps.crm.urls')),
    path('v0/assignment/', include('apps.assignment.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


admin.site.site_header = "Teamwork Admin"
admin.site.site_title = "Teamwork Admin Portal"
admin.site.index_title = "Welcome to Teamwork Admin Portal"
