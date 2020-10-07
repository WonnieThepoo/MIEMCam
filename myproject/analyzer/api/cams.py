import requests


def get_sources(key={"key": "9445980805164d5aa0efc6c91500d298"}):
    """
    Request to NVR, data param: {"uid" : int, "name" : str, "room"  : str}
    Return list of dict
    """
    response = []
    url = 'https://nvr.miem.hse.ru/api/rooms/'
    re = requests.get(url=url, headers=key)
    if re.status_code == 200:
        rooms = re.json()
        for room in rooms:
            for cam in room['sources']:
                cam_description = {'room': room['name'],
                                   'name': cam['name'],
                                   'uid': cam['id']}
                response.append(cam_description)
    return response


def get_room(key={"key": "9445980805164d5aa0efc6c91500d298"}):
    """
    Request to NVR (Uid, IP, port, login, password)
    Return list of dict
    """
    cams = []
    url = 'https://nvr.miem.hse.ru/api/sources/'
    re = requests.get(url=url, headers=key)
    if re.status_code == 200:
        re = re.json()
        for cam in re:
            cam_description = {'uid': cam['id'],
                               'port': cam['port'],
                               'ip': cam['ip'],
                               'login': 'admin',
                               'password': 'Supervisor'}
            cams.append(cam_description)
    return cams
