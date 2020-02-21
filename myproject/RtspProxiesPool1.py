import logging
logger = logging.getLogger(__name__)

from RtspProxy1 import RtspProxy1


class RtspProxiesPoolError(Exception):
    pass


class RtspProxiesPool1:
    def __init__(self, first_port=9000):
        self._first_port = first_port
        self._last_port = first_port
        self._proxies = {}

    def add_proxy(self, cam):
        uid = cam['uid']
        if uid in self._proxies:
            port = self._proxies[uid].get_port()
            self._proxies[uid].kill()
        else:
            port = self._last_port
            self._last_port += 1

        self._proxies[uid] = RtspProxy1(cam, port)
        self._proxies[uid].run()
        logger.info(f"Stream available at rtsp://0.0.0.0:{port}/{uid}")

    def stop_proxy(self, uid):
        self._proxies[uid].kill()
        port = self._proxies[uid].get_port()
        logger.info(f"Stream at rtsp://0.0.0.0:{port}/{uid} has stopped")

    def get_port(self, uid):
        """
        Cam avaliable at rtsp://server_ip:this_function_returned_port/camera_uid
        for example rtsp://172.18.201.34:9000/my_camera_uid
        """
        if uid in self._proxies:
            return self._proxies[uid].get_port()
        else:
            raise RtspProxiesPoolError('No cam with uri ' + str(uid))
