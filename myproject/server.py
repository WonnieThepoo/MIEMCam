from flask import Flask, request
from ONVIFCameraControl import ONVIFCameraControl as OCC
from functools import wraps

app = Flask(__name__)
cam = OCC(("172.18.200.51", 80), "admin", "Supervisor", "wsdl")
cams = {}
cams_in_room = {}
chosen_cam = ''

"""from sqlalchemy import Table, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import mapper

engine = create_engine('sqlite:///:memory:', echo=True)


metadata = MetaData()
cams_table = Table('cams', metadata,
               Column('uid', String(100), primary_key=True),
               Column('ip', String(30)),
               Column('port', Integer(10)),
               Column('user', String(50)),
               Column('password', String(50))
)
cam_room = Table('room', metadata,
             Column('idroom', String(10)),
             Column('uid', String(100), ForeignKey=True),
             Column('name', String(100))
)
metadata.create_all(engine)"""

"""class cams_(object):
    def __init__(self, name, fullname, password):
        self.name = name
        self.fullname = fullname
        self.password = password

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)
"""


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
    global chosen_cam
    data = request.json
    chosen_cam = data['uid']
    add_cams_in_room(data)
    uid_camobject(data)
    return 'ok'

def add_cams_in_room(data):
    global cams_in_room
    #проверка на существование комнаты, если таковой нет - создаёт её и вносит камеру со всей инфой
    if data['room'] not in cams_in_room.keys():
        cams_in_room[data['room']] = []
        add_uid_name(data)
    """
    Старый вариант, новый вроде работает отлично, но на всякий случай не буду удалять
    if data['uid'] not in cams_in_room.keys():
        uid_name_dict = {'uid': data['uid'],
                         'name': data['name']}
        cams_in_room[data['room']].append(uid_name_dict)"""
    #если комната существовала, то проверяет есть ли такая камера уже в ней по uid, если есть - не добавляет её
    """for b in cams.keys():  #оделать проход по комнатам и uid
        for c in cams[b]:
            if cams[b]['uid'] != data['uid']:
                add_uid_name(data)"""
    for b in cams_in_room[data['room']]:
        if b['uid'] != data['uid']:
            add_uid_name(data)
    print('Это камеры:', cams_in_room)

# добавление uid и name камер
def  add_uid_name(data):
    uid_name_dict = {'uid': data['uid'],
                     'name': data['name']}
    cams_in_room[data['room']].append(uid_name_dict)

def uid_camobject(data):
    global cams
    cam = OCC((data['addr']['ip'], data['addr']['port']), data['user'], data['password'])
    cams[data['uid']] = cam
    """json = json.dumps(cams)
    f = open('cams_in_room.json', 'w')
    f.write(json)
    f.close()"""

    print('Это камера сейчас', cams)

@app.route('/set_brightness', methods=['POST'])
@auth_required
def set_brightness():
    data = request.json
    cam = cams[chosen_cam]
    cam.set_brightness(data['bright'])

@app.route('/set_color_saturation', methods=['POST'])
@auth_required
def set_color_saturation():
    data = request.json
    cam = cams[chosen_cam]
    cam.set_color_saturation(data['s_col'])
    return 'ok'

@app.route('/set_contrast', methods=['POST'])
@auth_required
def set_contrast():
    data = request.json
    cam = cams[chosen_cam]
    cam.set_contrast(data['s_con'])
    return 'ok'

@app.route('/set_sharpness', methods=['POST'])
@auth_required
def set_sharpness():
    data = request.json
    cam = cams[chosen_cam]
    cam.set_sharpness(data['s_sha'])
    return 'ok'

@app.route('/set_focus_mode', methods=['POST'])
@auth_required
def set_focus_mode():
    data = request.json
    cam = cams[chosen_cam]
    cam.set_focus_mode(data['s_foc'])
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

@app.route('/get_brightness', methods=['GET'])
@auth_required
def get_brightness():
    cam = cams[chosen_cam]
    return (jsonify(info = cam.get_brightness()))

@app.route('/get_sharpness', methods=['GET'])
@auth_required
def get_sharpness():
    cam = cams[chosen_cam]
    return (jsonify(info = cam.get_sharpness()))

@app.route('/get_contrast', methods=['GET'])
@auth_required
def get_contrast():
    cam = cams[chosen_cam]
    return (jsonify(info = cam.get_contrast()))

@app.route('/')
def index():
    return 'kek', 200

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
