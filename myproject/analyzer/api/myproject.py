from flask import Flask, request, jsonify
from analyzer.api.ONVIFCameraControl import ONVIFCameraControl as OCC
from functools import wraps
from analyzer.db.sqldb import db, User, Presets
import json
import requests
import xml.etree.ElementTree as ET
import ast
import functools
import multiprocessing.pool
from analyzer.api.cams import get_room, get_sources

def timeout(max_timeout): #вроде не работал правильно, хотел найти другой способ таймаута
    """
    Timeout decorator, parameter in seconds.
    """
    def timeout_decorator(item):
        """
        Wrap the original function.
        """
        @functools.wraps(item)
        def func_wrapper(*args, **kwargs):
            """
            Closure for function.
            """
            pool = multiprocessing.pool.ThreadPool(processes=1)
            async_result = pool.apply_async(item, args, kwargs)
            # raises a TimeoutError if execution exceeds max_timeout
            return async_result.get(max_timeout)
        return func_wrapper
    return timeout_decorator


def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///flask_basics.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)
    return app


app = create_app()
db.create_all(app=create_app())
applictation = app


cams = get_room()
camss = {}
chosen_cam = ''
vmixCam = '172.18.191.12:8088'


def auth_required(f):
    """
        Декоратор для примера.
        Обязательно переписать под своё приложение.
    """
    @wraps(f)
    def _verify(*args):
        auth_headers = request.headers.get('token')
        invalid_msg = {
            'message': 'No such user',
            'autheticated': False
        }
        if db.session.query(User.id).filter_by(token=str(auth_headers)).scalar() is not None:
            return f(*args)
        return jsonify(invalid_msg), 401

    return _verify


@app.route('/return_cams', methods=['GET'])
def list_cams_desctiption():
    """
    Request to NVR, data param: {"uid" : uid, "name" : "cam_name", "room"  : "room_name"}
    Return list of dict
    """
    response = get_sources()
    return json.dumps(response)


@app.route('/chose_cam', methods=['POST'])
@auth_required
def chose_cam():
    """
    Data param: {"uid" : "uid of cam"}
    Choosing cam from dict of cams
    """
    global chosen_cam, camss
    data = request.json
    chosen_cam = data['uid']
    inf = list(filter(lambda unic: unic['uid'] == chosen_cam, cams))
    cam = OCC((inf[0]['ip'], int(inf[0]['port'])), inf[0]['login'], inf[0]['password'], '../../wsdl')
    camss[data['uid']] = cam
    return jsonify({'message': 'Okey'}), 200


@app.route('/set_brightness', methods=['POST'])
@auth_required
def set_brightness():
    """
    Data param: float in range [0, 100]
    :return: error or successful message
    Set brightness on cam
    """
    data = request.json
    cam = camss[chosen_cam]
    cam.set_brightness(data)
    return jsonify({'message': 'Okey'}), 200


@app.route('/set_color_saturation', methods=['POST'])
@auth_required
def set_color_saturation():
    """
    Data param: float in range [0, 100]
    :return: error or successful message
    Set color saturation on cam
    """
    data = request.json
    cam = camss[chosen_cam]
    cam.set_color_saturation(data)
    return jsonify({'message': 'Okey'}), 200


@app.route('/set_contrast', methods=['POST'])
@auth_required
def set_contrast():
    """
    Data param: float in range [0, 100]
    :return: error or successful message
    Set contrast on cam
    """
    data = request.json
    cam = camss[chosen_cam]
    cam.set_contrast(data)
    return jsonify({'message': 'Okey'}), 200


@app.route('/set_sharpness', methods=['POST'])
@auth_required
def set_sharpness():
    """
    Data param: float in range [0, 100]
    :return: error or successful message
    Set color sharpness on cam
    """
    data = request.json
    cam = camss[chosen_cam]
    cam.set_sharpness(data)
    return jsonify({'message': 'Okey'}), 200


@app.route('/set_focus_mode', methods=['POST'])
@auth_required
def set_focus_mode():
    """
    Data param: string "MANUAL" or "AUTO"
    :return: error or successful message
    Set focus mode on cam
    """
    data = request.json
    cam = camss[chosen_cam]
    cam.set_focus_mode(data)
    return jsonify({'message': 'Okey'}), 200


@app.route('/move_focus_continuous', methods=['POST'])
@auth_required
def move_focus_continuous():
    """
    Data param: float in range [0, 100]
    :return: error or successful message
    Cam focus changing
    """
    data = request.json
    cam = camss[chosen_cam]
    cam.move_focus_continuous(data['m_foc'])
    return jsonify({'message': 'Okey'}), 200


@app.route('/move_focus_absolute', methods=['POST'])
@auth_required
def move_focus_absolute():
    """
    Data param: {"m_foc":"float"} float in range of [-1, 1]
    :return: error or successful message
    Cam focus changing
    """
    data = request.json
    cam = camss[chosen_cam]
    cam.move_focus_absolute(data['m_focabs'])
    return jsonify({'message': 'Okey'}), 200


@app.route('/stop_focus', methods=['GET'])
@auth_required
def stop_focus():
    """
    :return: error or successful message
    Stop cam focus changing
    """
    cam = camss[chosen_cam]
    cam.stop_focus()
    return jsonify({'message': 'Okey'}), 200


@app.route('/set_preset', methods=['POST'])
@auth_required
def set_preset():
    """
    Data param: {"s_pres":"int"} int in range of [1, 9]
    :return: error or successful message
    Set preset of cam
     """
    data = request.json
    auth_headers = request.headers.get('token')
    user = db.session.query(User).filter_by(token=str(auth_headers)).first()
    userid = user.id
    print(user.id)
    pres_id = (userid - 1) * 9 + int(data['s_pres'])
    # не более 90 пресетов на 10 пользователей (из-за огринчений памяти камеры)
    if pres_id > 90:
        invalid_msg = {
            'message': 'Out of presets on cams',
            'autheticated': False
        }
        return jsonify(invalid_msg), 401
    if db.session.query(Presets.id).filter_by(user_id=userid,
                                              preset_on_cam_id=pres_id,
                                              uid_cam=chosen_cam).scalar() is None:

        new_preset = Presets(user_id=user.id,
                             uid_cam=int(chosen_cam),
                             button_clr=data['colour'],
                             preset_on_cam_id=pres_id)
        db.session.add(new_preset)
        db.session.commit()
    #elif db.session.query(Presets.id).filter_by(user_id=userid, preset_on_cam_id=pres_id, uid_cam=chosen_cam).scalar() is not None:
    else:
        db.session.query(User).filter(Presets.user_id == userid,
                                      Presets.preset_on_cam_id == pres_id,
                                      Presets.uid_cam == chosen_cam).update({Presets.uid_cam: chosen_cam}
                                                                            #{Presets.button_clr: data['color']},
                                                                            )
        db.session.commit()
    cam = camss[chosen_cam]
    cam.set_preset(data['s_pres'])
    return jsonify({'message': 'Okey'}), 200


@app.route('/goto_preset', methods=['POST'])
@auth_required
def goto_preset():
    """
    Data param: {"go_pres": int} int in range of [1, 90]
    :return: error or successful message
    Go to preset of cam
    """
    data = request.json
    auth_headers = request.headers.get('token')
    user = db.session.query(User).filter_by(token=str(auth_headers)).first()
    userid = user.id
    pres_id = (userid - 1) * 9 + int(data['go_pres'])
    cam = camss[chosen_cam]
    cam.goto_preset(pres_id)
    return jsonify({'message': 'Okey'}), 200


@app.route('/get_presets', methods=['GET'])
@auth_required
def get_presets():
    """
    Return presets of cam list of dict [{"uid": int}, {"colour": "str"}, {"number": int}]
    """
    auth_headers = request.headers.get('token')
    user = db.session.query(User).filter_by(token=str(auth_headers)).first()
    presets = db.session.query(Presets).filter(Presets.user_id == user.id, Presets.uid_cam == chosen_cam)
    presets_to_return = []
    for preset in presets:
        pre = {'uid': preset.uid_cam,
               'color': preset.button_clr,
               'number': preset.preset_on_cam_id - (user.id - 1) * 9
               }
        presets_to_return.append(pre)
    cam = camss[chosen_cam]
    cam.get_presets()
    return jsonify(presets_to_return), 200


@app.route('/continuous_move', methods=['POST'])
@auth_required
def move_continuous():
    """
    Data param: {"ptz": [float, float, float]} float in range of [-1, 1]
    :return: error or successful message
    Cam moving
    """
    data = request.json
    cam = camss[chosen_cam]
    cam.move_continuous(data['ptz'])
    return jsonify({'message': 'Okey'}), 200


@app.route('/move_relative', methods=['POST'])
@auth_required
def move_relative():
    """
    Data param: {"m_rel":[ float, float, float]} float in range of [-1, 1]
    :return: error or successful message
    Cam moving relative (Most of cams can't use it)
    """
    data = request.json
    cam = camss[chosen_cam]
    cam.move_relative(data['m_rel'])
    return jsonify({'message': 'Okey'}), 200


@app.route('/stop', methods=['GET'])
@auth_required
def stop():
    """
    :return: error or successful message
    Stop cam moving
    """
    cam = camss[chosen_cam]
    cam.stop()
    return jsonify({'message': 'Okey'}), 200


@app.route('/go_home', methods=['GET'])
@auth_required
def go_home():
    """
    :return: error or successful message
    Go to home preset
    """
    cam = camss[chosen_cam]
    cam.go_home()
    return jsonify({'message': 'Okey'}), 200


@app.route('/move_absolute', methods=['POST'])
@auth_required
def move_absolute():
    """
    Data param: {"m_rel":[ float, float, float]} float in range of [-1, 1]
    :return: error or successful message
    Cam moving absolute coord. (Most of cams can't use it)
    """
    data = request.json
    cam = camss[chosen_cam]
    cam.move_absolute(data(['m_abs']))
    return jsonify({'message': 'Okey'}), 200


@app.route('/login', methods=['POST'])
def login():
    """
    Data param: {"email": "string", "password": "string"}
    :return: {"token": "string"}
    Logging to NVR account (https://nvr.miem.hse.ru), getting NVR token,
    adding email, password, token to DataBase
    """
    data = request.json
    re = requests.post(url='https://nvr.miem.hse.ru/api/login', json=data)
    if re.status_code == 202:
        re = ast.literal_eval(re.content.decode('UTF-8'))
        token = re['token']
        if db.session.query(User.id).filter_by(email=data['email']).scalar() is None:
            new_user = User(email=data['email'],
                            password=data['password'],
                            token=token)
            db.session.add(new_user)
        else:
            db.session.query(User).filter(User.email == data['email']).update({User.token: token})
        db.session.commit()
        for instance in db.session.query(User).order_by(User.id):
            print(instance.email, instance.id, instance.token)
        return json.dumps(re)
    else:
        return json.dumps({'error': 'Something Wrong', 'authenticated': 'false'})


@app.route('/vmix', methods=['POST'])
def vmix():
    """
    Data param:{"Function": "string", "Input": "int"}
    :return: error or successful message
    request (with 1 or 2 arguments) to host with installed Vmix
    Read Vmix api here https://www.vmix.com/help19/index.htm?DeveloperAPI.html
    """

    responce = "http://" + vmixCam + "/API/?Function="
    data = request.json
    if len(data) == 1:
        responce += str(list(data.values())[0])
    elif len(data) == 2:
        responce += str(list(data.values())[0]) + '&Input=' + str(list(data.values())[1])
    else:
        return jsonify({"message": "error"}), 401
    requests.post(responce)
    return jsonify({"message": "successful"}), 200


@app.route('/vmixInfo', methods=['GET'])
def vmixInfo():
    """
    Data param: None
    :return: dict of with info about overlays/preview/active
    example {'overlay1': '2', 'overlay2': None, 'overlay3': None,
            'overlay4': None, 'overlay5': None, 'overlay6': None,
            'preview': '2', 'active': '3'}
    """
    response = requests.post('http://' + vmixCam + '/api/')
    tree = ET.fromstring(response.content)
    inf = {}
    for i in tree.find('overlays'):
        inf['overlay' + str(i.attrib['number'])] = i.text
    inf['preview'] = tree.find('preview').text
    inf['active'] = tree.find('active').text
    return json.dumps(inf), 200

@app.route('/chose_vmix', methods=['POST'])
def chose_vmix():
    """
    Data param: {"ip": "int", "port": "int"}
    :return: error or successful message
    request to change host with installed Vmix
    """
    global vmixCam
    data = request.json
    vmixCam = str(data['ip']) + ':' + str(data['port'])
    return jsonify({'message': 'Okey'}), 200

@app.route('/')
def index():
    return jsonify({'message': 'Okey'}), 200


if __name__ == '__main__':
    app.run(debug=True,
            host='0.0.0.0',
            #port=5000,
            threaded=False)
