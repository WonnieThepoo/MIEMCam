from flask import Flask, request
from ONVIFCameraControl import ONVIFCameraControl as OCC
from functools import wraps
from myproject.sqldb import db, User, TCam, Room
from werkzeug.security import generate_passworod_hash, check_password_hash
from googleapiclient.discovery import build
from google.oauth2 import service_account
import json



def create_app():
    app = Flask(__name__)

    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_basics.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    return app
app = create_app()
db.create_all(app=create_app())


#cam = OCC(("172.18.200.56", 80), "admin", "Supervisor", "wsdl")
cams = {}
cams_in_room = {}
chosen_cam = ''


def auth_required(f):
    """Проверка аунтификации"""
    @wraps(f)
    def _verify(*args, **kwargs):
        auth_headers = request.headers['key']

        invalid_msg = {
            'message': 'Неверный ключ аунт',
            'autheticated': False
        }

        token = auth_headers
        if token == '9445980805164d5aa0efc6c91500d298':
            return f(*args, **kwargs)

        return invalid_msg, 401

    return _verify


def get_cameras_list():
    SCOPES = ['https://www.googleapis.com/auth/admin.directory.resource.calendar.readonly',
                  'https://www.googleapis.com/auth/admin.directory.resource.calendar']
    SERVICE_ACCOUNT_FILE = 'visca-onvif-converter-20020854b334.json'
    with open('gsuit_domain_account.txt') as file:
        GSUIT_DOMAIN_ACCOUNT = file.readline()

    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
    delegated_credentials = credentials.with_subject(GSUIT_DOMAIN_ACCOUNT)
    service = build('admin', 'directory_v1', credentials=delegated_credentials)
    results = service.resources().calendars().list(customer='C03s7v7u4').execute()
    cameras = []
    for i in results['items']:
        if i['resourceType'] == 'ONVIF-camera':
            cameras.append(i)
    return cameras

@app.route('/return_cams', methods=['GET'])
@auth_required
def list_cams_desctiption():
    cameras = get_cameras_list()
    response = []
    for cam in cameras:
        cam_description = {}
        cam_description['room'] = cam['floorSection']
        cam_description['name'] = cam['resourceName']
        cam_description['uid'] = cam['resourceId']
        response.append(cam_description)
    return json.dumps(response)




@app.route('/chose_cam', methods=['POST'])
@auth_required
def chose_cam():
    global chosen_cam
    data=request.json
    chosen_cam = data['uid']
    print('Это камера сейчас', chosen_cam)
    return 'ok'

@app.route('/set_cam', methods=['POST'])
@auth_required
def set_cam():
    data = request.get_json()
    new_cam = TCam(uid=data['uid'])
    new_cam.ip = data['addr']['ip']
    new_cam.port = data['addr']['port']
    new_cam.user = data['user']
    new_cam.password = data['password']
    db.session.add(new_cam)
    db.session.commit()
    new_room = Room(idr=data['room'])
    new_room.cam_name = data['name']
    db.session.add(new_room)
    db.session.commit()
    return 'ok'



"""@app.route('/del_cam', methods=['DELETE'])
@auth_required
def del_cam():
    uid = request.get_json()
    d_cam = TCam.query.get(uid)
    print(d_cam)
    db.session.delete(d_cam)
    db.session.commit()
    return 'ok'"""

"""def add_cams_in_room(data):
    global cams_in_room
    #проверка на существование комнаты, если таковой нет - создаёт её и вносит камеру со всей инфой
    if data['room'] not in cams_in_room.keys():
        cams_in_room[data['room']] = []
        add_uid_name(data)
    for b in cams_in_room[data['room']]:
        if b['uid'] != data['uid']:
            add_uid_name(data)
    print('Это камеры:', cams_in_room)"""

# добавление uid и name камер
"""def  add_uid_name(data):
    uid_name_dict = {'uid': data['uid'],
                     'name': data['name']}
    cams_in_room[data['room']].append(uid_name_dict)

def uid_camobject(data):
    global cams
    cam = OCC((data['addr']['ip'], data['addr']['port']), data['user'], data['password'])
    cams[data['uid']] = cam

    print('Это камера сейчас', cams)"""

@app.route('/set_brightness', methods=['POST'])
@auth_required
def set_brightness():
    data = request.json
    cam = cams[chosen_cam]
    cam.set_brightness(data)
    return 'ok'

@app.route('/set_color_saturation', methods=['POST'])
@auth_required
def set_color_saturation():
    data = request.json
    cam = cams[chosen_cam]
    cam.set_color_saturation(data)
    return 'ok'

@app.route('/set_contrast', methods=['POST'])
@auth_required
def set_contrast():
    data = request.json
    cam = cams[chosen_cam]
    cam.set_contrast(data)
    return 'ok'

@app.route('/set_sharpness', methods=['POST'])
@auth_required
def set_sharpness():
    data = request.json
    cam = cams[chosen_cam]
    cam.set_sharpness(data)
    return 'ok'

@app.route('/set_focus_mode', methods=['POST'])
@auth_required
def set_focus_mode():
    data = request.json
    cam = cams[chosen_cam]
    cam.set_focus_mode(data)
    return 'ok'

@app.route('/move_focus_continuous', methods=['POST'])
@auth_required
def move_focus_continuous():
    data = request.json
    cam = cams[chosen_cam]
    cam.move_focus_continuous(data['m_foc'])
    return 'ok'

@app.route('/move_focus_absolute', methods=['POST'])
@auth_required
def move_focus_absolute():
    data = request.json
    cam = cams[chosen_cam]
    cam.move_focus_absolute(data['m_focabs'])
    return 'ok'

@app.route('/stop_focus', methods=['POST'])
@auth_required
def stop_focus():
    cam = cams[chosen_cam]
    cam.stop_focus()
    return 'ok'

@app.route('/set_preset', methods=['POST'])
@auth_required
def set_preset():
    data = request.json
    cam = cams[chosen_cam]
    cam.set_preset(data['s_pres'])
    return 'ok'

@app.route('/goto_preset', methods=['POST'])
@auth_required
def goto_preset():
    data = request.json
    cam = cams[chosen_cam]
    cam.goto_preset(data['go_pres'])
    return 'ok'

@app.route('/get_presets', methods=['GET'])
@auth_required
def get_presets():
    cam = cams[chosen_cam]
    cam.get_presets()
    return 'ok'

@app.route('/continuous_move', methods=['POST'])
@auth_required
def move_continuous():
    data = request.json
    cam = cams[chosen_cam]
    cam.move_continuous(data['ptz'])
    return 'ok'
a=[]
newCams = []
for (room, cameras) in a:
    for camera in cameras:
        newCamera = camera
        newCamera["room"]=room
        newCams.add(camera)

@app.route('/move_relative', methods=['POST'])
@auth_required
def move_relative():
    data = request.json
    cam = cams[chosen_cam]
    cam.move_relative(data['m_rel'])
    return 'ok'

@app.route('/stop', methods=['GET'])
@auth_required
def stop():
    cam = cams[chosen_cam]
    cam.stop()
    return 'ok'

@app.route('/go_home', methods=['GET'])
@auth_required
def go_home():
    cam = cams[chosen_cam]
    cam.go_home()
    return 'ok'

@app.route('/move_absolute', methods=['POST'])
@auth_required
def move_absolute():
    data = request.json
    cam = cams[chosen_cam]
    cam.move_absolute(data(['m_abs']))
    return 'ok'

@app.route('/__get_move_options', methods=['GET'])
@auth_required
def __get_move_options():
    cam = cams[chosen_cam]
    cam.__get_move_options()
    return 'ok'

@app.route('/__get_video_sources', methods=['GET'])
@auth_required
def __get_video_sources():
    cam = cams[chosen_cam]
    cam.__get_video_sources()
    return 'ok'

@app.route('/__get_options', methods=['GET'])
@auth_required
def __get_options():
    cam = cams[chosen_cam]
    cam.__get_options()
    return 'ok'

@app.route('/__get_ptz_conf_opts', methods=['GET'])
@auth_required
def __get_ptz_conf_opts():
    cam = cams[chosen_cam]
    cam.__get_ptz_conf_opts()
    return 'ok'

@app.route('/__get_configurations', methods=['GET'])
@auth_required
def __get_configurations():
    cam = cams[chosen_cam]
    cam.__get_configurations()
    return 'ok'

@app.route('/__get_node', methods=['GET'])
@auth_required
def __get_node():
    cam = cams[chosen_cam]
    cam.__get_node()
    return 'ok'

@app.route('/__set_imaging_settings', methods=['SET'])
@auth_required
def __set_imaging_settings():
    data = request.json
    cam = cams[chosen_cam]
    cam.__set_imaging_settings(data['s_set'])
    return 'ok'

@app.route('/__get_imaging_settings', methods=['GET'])
@auth_required
def __get_imaging_settings():
    cam = cams[chosen_cam]
    cam.__get_imaging_settings()
    return 'ok'

@app.route('/')
def index():
    return 'kek', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80, threaded=False)

