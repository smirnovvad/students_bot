import requests
from settings import API_URL
HOST = API_URL


def tglogin_api(id):
    r = requests.post(f'{HOST}/auth', json={'telegram_id': id})
    # print(r.json)
    return r.json(), r.status_code


def get_groups(access_token):
    r = requests.get(f'{HOST}/group', headers={'Authorization': f'Bearer {access_token}'})
    # print(r.json)
    return r.json(), r.status_code


def get_detail(access_token, link):
    r = requests.get(f'{HOST}{link}', headers={'Authorization': f'Bearer {access_token}'})
    # print(r.json)
    return r.json(), r.status_code


def update(access_token, link, data):
    r = requests.put(f'{HOST}{link}', headers={'Authorization': f'Bearer {access_token}'}, json=data)
    # print(r.json)

    return r.json(), r.status_code
