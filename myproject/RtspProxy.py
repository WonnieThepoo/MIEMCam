import logging
logger = logging.getLogger(__name__)

import subprocess
import time
import os
import signal

class RtspProxy:
    def __init__(self, inf, server_port):
        self._server_port = server_port
        print(inf)
        self._server_uri = 'rtsp://0.0.0.0:' + str(server_port) + '/' + inf[0]['uid']
        self._camera_uri = 'rtsp://' + inf[0]['login'] + ':' + inf[0]['password'] + '@' + (inf[0]['ip'])
        self._process = None

    def run(self):
        logger.debug(f'Run vlc subprocess, cam:{self._camera_uri} on {self._server_uri} ')
        shell_command = ('vlc -I dummy ' +
                         '{} '.format(self._camera_uri) +
                         "--sout '#rtp{sdp=" + self._server_uri + ",caching=0}' " +
                         '--sout-keep ')
        self._process = subprocess.Popen(shell_command, shell=True,
                                         stdout=subprocess.PIPE,
                                         preexec_fn=os.setsid)

    def is_alive(self):
        if self._process is None:
            return False
        return not self._process.poll()

    def kill(self):
        logger.debug(f'Kill vlc subprocess, cam:{self._camera_uri} on {self._server_uri} ')
        if self.is_alive():
            os.killpg(os.getpgid(self._process.pid), signal.SIGTERM)
            self._process.wait()

    def get_port(self):
        if self._process is not None:
            return self._server_port

    def __del__(self):
        self.kill()
