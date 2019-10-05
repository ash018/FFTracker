from django.urls import path
from apps.location.views import UploadLocation, ResourceLocationList, \
    SearchLocationsMap, ResourceHistory, BatchUploadLocation


LOC_URLS = {
    'upload_location_api': 'agent/',
    'get_resource_locations': 'manager/get/',
    'search_locations_map': 'search/map/',
    'search_locations_preferred': 'search/preferred/',
    'get_resource_history': 'manager/history/',
    'batch_upload_location': 'agent/batch/',
}


urlpatterns = [
    path(LOC_URLS['upload_location_api'], UploadLocation.as_view()),
    path(LOC_URLS['get_resource_locations'], ResourceLocationList.as_view()),
    path(LOC_URLS['search_locations_map'], SearchLocationsMap.as_view()),
    path(LOC_URLS['get_resource_history'], ResourceHistory.as_view()),
    path(LOC_URLS['batch_upload_location'], BatchUploadLocation.as_view()),
]