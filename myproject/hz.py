from RtspProxiesPool1 import RtspProxiesPool1

cams = [
    {
        "addr":
            {
                "ip": "172.18.191.24",
                "port": 80
            },
        "user": "admin",
        "password": "Supervisor",
        "room": "504",
        "uid": "2",
        "name": "2134"
    },
]

if __name__ == '__main__':

    rtspProxiesPool = RtspProxiesPool1()

    for cam in cams:
        rtspProxiesPool.add_proxy(cam)
        uid = cam['uid']
        port = rtspProxiesPool.get_port(uid)  # More information at this function docstring
        print(port, cam['uid'])

    print('Press enter to end proxying')
    input()
