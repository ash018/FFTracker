from django.urls import path
from apps.report.views import TaskCombined, AttendanceFiltered, AttendanceIndividual, \
    AttendanceCombined, Rankings, TaskExport, AttendanceExport, TaskFilteredList


REPORT_URLS = {
    'task_combined': 'task/',
    'task_filtered': 'task/list/',
    'task_export': 'task/export/',
    'attendance_combined': 'attendance/',
    'attendance_filtered': 'attendance/list/',
    'attendance_individual': 'attendance/user/',
    'attendance_export': 'attendance/export/',
    'rankings': 'rankings/',
}


urlpatterns = [
    path(REPORT_URLS['task_combined'], TaskCombined.as_view()),
    path(REPORT_URLS['task_filtered'], TaskFilteredList.as_view()),
    path(REPORT_URLS['attendance_combined'], AttendanceCombined.as_view()),
    path(REPORT_URLS['attendance_filtered'], AttendanceFiltered.as_view()),
    path(REPORT_URLS['attendance_individual'], AttendanceIndividual.as_view()),
    path(REPORT_URLS['rankings'], Rankings.as_view()),
    path(REPORT_URLS['task_export'], TaskExport.as_view()),
    path(REPORT_URLS['attendance_export'], AttendanceExport.as_view()),
]