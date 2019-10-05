import requests

LOC_API = 'https://api.dingi.live/maps/v2/search/region/'
REV_GEOCODE_URL = 'https://api.dingi.live/maps/v2/reverse'


EVENT_DICT = {
    'To Online': 0,
    'On Task': 1,
    'No Task': 2,
    'To Offline': 3,
    'To OOC': 4,
    'Start task': 5,
    'Finish task': 6,
    'Off OOC': 7,
    'In OOC': 8,
    'Ping Server': 21,
}

EVENT_CHOICES = tuple((value, key) for key, value in EVENT_DICT.items())


# Task Data Helpers
def get_address(lat, lng):
    params = {'language': 'en', 'lat': lat, 'lng': lng}
    headers = {'x-api-key': 'jjNLDbFupjaHxhUozDBTj966XLLxzFKS4VOxEIkz'}
    try:
        response = requests.get(REV_GEOCODE_URL, params=params, headers=headers)
        address = response.json()['result']['address']
    except:
        address = ''
    return address


def get_locations(token):
    params = {'query_string': token}
    headers = {'x-api-key': 'jjNLDbFupjaHxhUozDBTj966XLLxzFKS4VOxEIkz'}
    place_list = []
    try:
        response = requests.get(LOC_API, headers=headers, params=params)
        places = response.json()['search_result']
        # print(places)
        idx = 0
        for place in places:
            place_list.append({
                'id': idx,
                'name': place['name'],
                'point': place['rep_point']
            })
            idx += 1
    except Exception as e:
        print(">>Location search exceptions: " + str(e))
    return place_list
