import requests
from math import sin, cos, sqrt, atan2, radians


def get_geo_info(city_name, type_info):
    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        'geocode': city_name,
        'format': 'json',
        'apikey': "40d1649f-0493-4b70-98ba-98533de7710b"  # Устаревший API Key!
    }

    try:
        response = requests.get(url, params)
        response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
        json_data = response.json()

        if type_info == 'country':
            return json_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject'][
                'metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['CountryName']
        elif type_info == 'coordinates':
            point_str = json_data['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
            point_array = [float(x) for x in point_str.split(' ')]
            return point_array
        else:
            print(f"Error: Invalid type_info: {type_info}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None
    except (KeyError, IndexError) as e:
        print(f"Error parsing JSON response: {e}")
        return None


def get_distance(p1, p2):
    R = 6373.0

    lon1 = radians(p1[0])
    lat1 = radians(p1[1])
    lon2 = radians(p2[0])
    lat2 = radians(p2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance


if __name__ == '__main__':
    city = "Москва"
    country = get_geo_info(city, 'country')
    coordinates = get_geo_info(city, 'coordinates')

    if country:
        print(f"Страна для города {city}: {country}")
    else:
        print(f"Не удалось получить страну для города {city}")

    if coordinates:
        print(f"Координаты для города {city}: {coordinates}")
    else:
        print(f"Не удалось получить координаты для города {city}")

    city1 = "Москва"
    city2 = "Санкт-Петербург"
    coord1 = get_geo_info(city1, 'coordinates')
    coord2 = get_geo_info(city2, 'coordinates')

    if coord1 and coord2:
        distance = get_distance(coord1, coord2)
        print(f"Расстояние между {city1} и {city2}: {distance} км")
    else:
        print(f"Не удалось получить координаты для {city1} или {city2}")
