from datetime import datetime


def ow_geocode_mock(**params: object):
    url = 'https://api.openweathermap.org/geo/1.0/direct'
    url += f'?appid={params.get("appid", "dummy")}'
    url += f'&lang={params.get("lang", "en")}'
    url += '&limit=1'
    url += f'&q={params.get("city", "London")}%252C+{params.get("country", "UK")}'
    url += f'&units={params.get("units", "metric")}'

    print(url)

    response = [
        {
            'name': params.get('city', 'London'),
            'country': params.get('country', 'UK'),
            'lat': params.get('lat', 51.5074),
            'lon': params.get('lon', -0.1278),
        }
    ]

    return url, response


def ow_timemachine_mock(**params: object):
    timestamp = int(datetime.strptime(str(params.get('day', '2024-01-01')), '%Y-%m-%d').timestamp())

    url = 'https://api.openweathermap.org/data/3.0/onecall/timemachine'
    url += f'?appid={params.get("appid", "dummy")}'
    url += f'&dt={params.get("dt", timestamp)}'
    url += f'&lang={params.get("lang", "en")}'
    url += f'&lat={params.get("lat", 51.5074)}'
    url += f'&lon={params.get("lon", -0.1278)}'
    url += f'&units={params.get("units", "metric")}'

    response = {
        'data': [
            {
                'temp': params.get('temp', 15.5),
                'weather': [{'description': params.get('description', 'Sunny')}],
            }
        ]
    }

    return url, response


def ow_error(**params: object):
    return {
        'cod': params.get('code', 401),
        'message': params.get('message', 'Error'),
    }
