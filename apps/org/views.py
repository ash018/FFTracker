from django.db import transaction
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from apps.user.permissions import is_organizer, is_manager
from rest_framework.permissions import AllowAny, IsAuthenticated

from apps.org.models import Organization
from apps.org.serializers import OrgSerializer
from apps.org.helpers import *

from apps.user.auth_helpers import check_oid_exists
from apps.location.models import ClientLocation


class OrganizationViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk, format=None):
        """
        Response:
        ---
            {
                'packages': PACKAGE_INFO,
                'oid': org.oid,
                'org_id': org.id,
                'org_name': org.org_name,
                'org_address': org.address,
                'package_info': {},

                'renew_needed': renew_needed,
                'day_start': str(org.day_start),
                'day_end': str(org.day_end),
                'location_interval': org.location_interval,
                'min_work_hour_p': org.min_work_hour_p,
                'weekend': org.weekend,
                'logo': org.logo,
                'tracking_enabled': org.tracking_enabled,
            }
        """
        is_manager(request)
        if Organization.objects.filter(id=pk).exists():
            org = Organization.objects.get(id=pk)
            organization_details = get_org_details(org)
            # print(organizer_details)
            return Response(organization_details, status=200)
        resp = {'detail': "organization not found."}
        return Response(resp, status=400)

    def update(self, request, pk, format=None):
        """
        Sample Submit:
        ---
            {
                'org_name': 'org1',
                'address': 'Badda link road',
                'day_start': '09:00:00'',
                'day_end': '17:00:00',
                'location_interval': 120,
                'logo': 'logo_url..',
                'min_work_hour_p': 90,
                'weekend': [4, 5],
                'tracking_enabled': true,
            }

        Response:
        ---
            same as profile
        """
        is_organizer(request)
        user = request.user

        serializer = OrgSerializer(data=request.data)
        if serializer.is_valid():
            org = Organization.objects.get(id=pk)
            if user.org != org:
                data = {'detail': 'Forbidden!'}
                return Response(data, status=403)
            serializer.org_update(org, serializer.validated_data)
            data = {'msg': 'OK'}
            return Response(data, status=200)
        # print(serializer.errors)
        return Response({'detail': str(serializer.errors)}, status=400)

    # def delete(self, request, pk, format=None):


class DeleteAccount(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        is_organizer(request)
        organizer = request.user
        org = organizer.org
        try:
            with transaction.atomic():
                organizer.delete()
                org.status = 2 # suspended
                org.save()
                return Response({'msg': 'OK'}, status=200)
        except Exception as e:
            return Response({'detail': str(e)}, status=400)


class UserExcelUpload(APIView):
    # TODO: change to authenticated
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
            Sample form:
            ---
                'user_data': file(excel file for team data)

        """
        is_organizer(request)
        organizer = request.user

        # fetching csv file
        # print(request.FILES)
        excel_file = request.FILES.get("user_data", None)
        validate_excel(excel_file)

        user_list = check_team_hierarchy_excel(excel_file, organizer)
        with transaction.atomic():
            create_teams_sync(user_list, organizer)
        resp = {
            'msg': 'Upload Process finished'
        }
        return Response(resp, status=200)


class UserCSVUpload(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
            Sample form:
            ---
                'user_data': file(csv file for user data)

        """
        is_organizer(request)
        organizer = request.user

        # fetching csv file
        # print(request.FILES)
        csv_file = request.FILES.get("user_data", None)
        validate_csv(csv_file)

        user_list = check_team_hierarchy_csv(csv_file, organizer)
        with transaction.atomic():
            create_teams_sync(user_list, organizer)
        resp = {
            'msg': 'Upload Process finished'
        }
        return Response(resp, status=200)


class TaskExcelUpload(APIView):
    # TODO: change to authenticated
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
            Sample form:
            ---
                'task_data': file(excel file for team data)

        """
        # is_organizer(request)
        user = request.user

        # fetching csv file
        excel_file = request.FILES.get("task_data", None)
        validate_excel(excel_file)

        task_list = check_tasks_excel(excel_file, user)
        with transaction.atomic():
            create_tasks_sync(task_list, user)
        resp = {
            'msg': 'Upload Process finished'
        }
        return Response(resp, status=200)


class TaskCSVUpload(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
            Sample form:
            ---
                'task_data': file(excel file for team data)

        """
        is_organizer(request)
        organizer = request.user

        # fetching csv file
        csv_file = request.FILES.get("task_data", None)
        validate_csv(csv_file)

        task_list = check_tasks_csv(csv_file, organizer)
        with transaction.atomic():
            create_tasks_sync(task_list, organizer)
        resp = {
            'msg': 'Upload Process finished'
        }
        return Response(resp, status=200)


class ClientLocationViewSet(viewsets.ViewSet):
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request, pk, format=None):
        """

        Sample response:
        ---
            {
                'id': loc.id,
                'name': loc.name,
                'address': loc.address,
                'point': {
                    'lat': 23.12341234,
                    'lon': 90.21341232
                }
            }

        """
        if ClientLocation.objects.filter(id=pk):
            loc = ClientLocation.objects.get(id=pk)
            location_details = get_location_obj(loc)
            # print(location_details)
            return Response(location_details, status=200)
        return Response({'msg': 'Location not found!'}, status=400)

    def list(self, request, format=None):
        """

        Sample response:
        ---
            [
                {
                    'id': 1,
                    'name': loc.name,
                    'address': loc.address,
                    'point': {
                        'lat': 23.12341234,
                        'lon': 90.21341232
                    }
                },
                {
                    'id': 2,
                    'name': loc.name,
                    'address': loc.address,
                    'point': {
                        'lat': 23.12341234,
                        'lon': 90.21341232
                    }
                },

            ]


        """
        user = request.user

        locs = ClientLocation.objects.filter(Q(org=user.org))

        location_list = get_location_list(locs)

        return Response(location_list, status=200)


class LocationExcelUpload(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        """
            Sample form:
            ---
                'location_data': file(excel file for team data)

        """
        is_organizer(request)
        organizer = request.user

        # fetching csv file
        excel_file = request.FILES.get("location_data", None)
        validate_excel(excel_file)

        location_list = check_locations_excel(excel_file)

        with transaction.atomic():
            create_locations_sync(location_list, organizer)
        resp = {
            'msg': 'Upload Process finished'
        }
        return Response(resp, status=200)


class LocationCSVUpload(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request, format=None):
        """
            Sample form:
            ---
                'location_data': file(excel file for team data)

        """
        is_organizer(request)
        organizer = request.user

        # fetching csv file
        csv_file = request.FILES.get("location_data", None)
        validate_csv(csv_file)

        location_list = check_locations_csv(csv_file)

        with transaction.atomic():
            create_locations_sync(location_list, organizer)
        resp = {
            'msg': 'Upload Process finished'
        }
        return Response(resp, status=200)


class OrgUrl(APIView):
    permission_classes = (AllowAny,)

    def get(self, request, url, format=None):
        """
        Sample Response:
        ---
            {
                'oid': 'url..',
                'org_name': '
                'logo': 'logo url..',
            }

        """
        url = url.lower()
        if check_oid_exists(url):
            org = Organization.objects.get(oid=url)
            data = {
                'oid': org.oid,
                'org_name': org.org_name,
                'logo': org.logo,
            }
            return Response(data, status=200)
        return Response({'detail': 'Organization not found!'}, status=404)





