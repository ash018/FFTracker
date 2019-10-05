from django.db import transaction
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.location.serializers import LocationSerializer
from apps.location.config import get_locations
from apps.location.executors import *

from apps.user.models import User
from apps.user.permissions import is_manager


class UploadLocation(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Parameter details:
        ---
            timestamp:
                type: datetime string
                required: Yes
            event:
                type: int
                required: Yes
                choices:
                    (0, 'To Online'),
                    (1, 'On Task'),
                    (2, 'No Task'),
                    (3, 'To Offline'),
                    (4, 'To OOC'),
                    (5, 'Start task'),
                    (6, 'Finish task'),
                    (7, 'Off OOC'),
                    (8, 'In OOC'),
            point:
                type: json object
                required: Yes
                example: {'lat': 23.780926, 'lng': 90.422858}
        """
        serializer = LocationSerializer(data=request.data)
        if serializer.is_valid():
            data = serializer.upload_location(
                    serializer.validated_data, request
            )
            if not data:
                return Response({'detail': 'Something went wrong!'}, status=400)
            return Response(data, status=200)
        return Response(serializer.errors, status=400)


class BatchUploadLocation(APIView):
    permission_classes = (IsAuthenticated,)

    def post(self, request, format=None):
        """
        Sample Submit:
        ---
            {
                "points": [
                     {
                        timestamp: '2018-12-03 16:28:48.464495',
                        point: {'lat': 23.780926, 'lng': 90.422858},
                        event: 8
                     },...
                ]
            }
        """

        agent_id = request.user.id
        locations = request.data.get('points', False)
        if not locations:
            return Response({'detail': 'Location not found!'}, status=400)
        mac = request.data.get('mac', '')
        upload_offline_locations(agent_id, locations, mac)
        return Response({'msg': 'OK'}, status=200)


class ResourceLocationList(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            agent_id:
                type: int
                required: No

        Sample Response:
        ---
            {
              [
                {
                    'point': {'lat': 23.1234, 'lng': 92.323},
                    'agent_id': 2,
                    'agent_name': 'name1',
                    'task_id': 12,
                    'task_title': 'title',
                    'event': 1,
                    'timestamp': '12-12-12 12:23:2323'
                },...
              ]
            }
        """
        is_manager(request)
        location_list = get_agent_locations(request)
        return Response(location_list, status=200)


class ResourceHistory(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Parameter details:
        ---
            agent_id:
                type: int
                required: Yes
            date:
                type: date string
                default: Current date

        Sample Response:
        ---
            {
              "location_list": [
                {
                    'point': {'lat': 23.1234, 'lng': 92.323},
                    'agent_id': 2,
                    'agent_name': 'name1',
                    'task_id': 12,
                    'task_title': 'title',
                    'event': 1,
                    'timestamp': '12-12-12 12:23:2323'
                },...
              ],

              "task_list": [
                    {
                        'id': 11,
                        'title': 'Title1',
                        'point': {
                                'lat':0,
                                'lng': 0
                            },
                        'status': 0,
                        'start': datetime,
                        'duration': 4,
                        'deadline': datetime,
                        'task_type': 'Doctors visit',
                        'agent_list': [50, 51],
                        'manager': 'name',
                        'custom_fields': [],
                        'address': 'address'
                    },...
              ]
            }

        """
        viewer = request.user
        agent_id = request.query_params.get('agent_id', False)
        date = request.query_params.get('date', False)
        if (not agent_id) or (not User.objects.filter(id=agent_id).exists()):
            return Response({'msg': 'Agent not found'}, status=400)

        if not date:
            return Response({'msg': 'Date not provided'}, status=400)

        agent = User.objects.get(id=agent_id)
        if agent.org != viewer.org:
            return Response({'msg': 'Forbidden'}, status=403)

        location_list, task_list = get_resource_history(agent, date)
        data = {
            'task_list': task_list,
            'location_list': location_list
        }
        return Response(data, status=200)


class SearchLocationsMap(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, format=None):
        """
        Query Parameter:
        ---
            token:
                type: str
                required: Yes

         Sample Response:
         ---
            {
              "place_list": [
                {
                  "id": 0,
                  "name": "Azimpur",
                  "point": {
                    "lat": 23.72826678172602,
                    "lon": 90.38520903921811
                  }
                },
                {
                  "id": 1,
                  "name": "South Azampur",
                  "point": {
                    "lat": 22.39708115000006,
                    "lon": 91.3914753784847
                  }
                },
                {
                  "id": 2,
                  "name": "Madhya Azampur",
                  "point": {
                    "lat": 25.72586263300006,
                    "lon": 88.60483423588528
                  }
                },
                ......
              ]
            }

        """
        # is_manager(request)
        token = request.GET.get('token', False)
        if token:
            place_list = get_locations(token)
            return Response({'place_list': place_list}, status=200)
        return Response({'message': 'No token found!'}, status=400)
