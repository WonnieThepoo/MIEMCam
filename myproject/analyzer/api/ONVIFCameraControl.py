import logging
logger = logging.getLogger(__name__)

import zeep
from onvif import ONVIFCamera
from copy import deepcopy
from analyzer.api.vector3 import vector3
from analyzer.api import common
from datetime import timedelta


# monkey patch
def zeep_pythonvalue(self, xmlvalue):
    return xmlvalue


zeep.xsd.simple.AnySimpleType.pythonvalue = zeep_pythonvalue


class ONVIFCameraControl:
    def __init__(self, addr, login, password, wsdl_path='wsdl'):
        common.check_addr(addr)
        logger.info(f'Initializing camera {addr}')

        self.cam = ONVIFCamera(addr[0], addr[1], login, password, wsdl_path)

        self.media_service = self.cam.create_media_service()
        self.ptz_service = self.cam.create_ptz_service()
        self.imaging_service = self.cam.create_imaging_service()

        self.profile = self.media_service.GetProfiles()[0]
        self.video_source = self.__get_video_sources()[0]

        self.status = self.ptz_service.GetStatus({'ProfileToken': self.profile.token})
        self.move_options = self.__get_move_options()

        logging.info(f'Initialized camera at {addr} successfully')

    def __ignore_exception(func):
            def wrapped(self, *args):
                try:
                    return func(self, *args)
                except Exception:
                    pass
            return wrapped

    def get_stream_uri(self, protocol='UDP', stream='RTP-Unicast'):
        """
        :param protocol
            string 'UDP', 'TCP', 'RTSP', 'HTTP'
        :param stream
             string either 'RTP-Unicast' or 'RTP-Multicast'
        WARNING!!!
        Some cameras return invalid stream uri

        RTP unicast over UDP: StreamType = "RTP_unicast", TransportProtocol = "UDP"
        RTP over RTSP over HTTP over TCP: StreamType = "RTP_unicast", TransportProtocol = "HTTP"
        RTP over RTSP over TCP: StreamType = "RTP_unicast", TransportProtocol = "RTSP"
        """
        logger.info(f'Getting stream uri {protocol} {stream}')
        request = self.media_service.create_type('GetStreamUri')
        request.ProfileToken = self.profile.token
        request.StreamSetup = {'Stream': stream, 'Transport': {'Protocol': protocol}}
        return self.media_service.GetStreamUri(request)

    @__ignore_exception
    def set_brightness(self, brightness=50):
        """
        :param brightness:
            float in range [0, 100]
        """
        logger.info(f'Settings brightness')
        imaging_settings = self.__get_imaging_settings()
        imaging_settings.Brightness = brightness
        self.__set_imaging_settings(imaging_settings)

    @__ignore_exception
    def set_color_saturation(self, color_saturation=50):
        """
        :param color_saturation:
            float in range [0, 100]
        """
        logger.info(f'Settings color_saturation')
        imaging_settings = self.__get_imaging_settings()
        imaging_settings.ColorSaturation = color_saturation
        self.__set_imaging_settings(imaging_settings)

    @__ignore_exception
    def set_contrast(self, contrast=50):
        """
        :param contrast:
            float in range [0, 100]
        """
        logger.info(f'Settings contrast')
        imaging_settings = self.__get_imaging_settings()
        imaging_settings.Contrast = contrast
        self.__set_imaging_settings(imaging_settings)

    @__ignore_exception
    def set_sharpness(self, sharpness=50):
        """
        :param sharpness:
            float in range [0, 100]
        """
        logger.info(f'Settings sharpness')
        imaging_settings = self.__get_imaging_settings()
        imaging_settings.Sharpness = sharpness
        self.__set_imaging_settings(imaging_settings)

    @__ignore_exception
    def set_focus_mode(self, mode='AUTO'):
        """
        :param mode:
            string, can be either 'AUTO' or 'MANUAL'
        """
        logger.info(f'Settings focus mode')
        imaging_settings = self.__get_imaging_settings()
        imaging_settings.Focus.AutoFocusMode = mode
        self.__set_imaging_settings(imaging_settings)


    @__ignore_exception
    def move_focus_continuous(self, speed):
        """
        :param speed:
            float in range [-1,1]
        """
        logger.info(f'Doing move focus continuous')
        request = self.imaging_service.create_type('Move')
        request.VideoSourceToken = self.video_source.token
        request.Focus = self.move_options
        request.Focus.Continuous.Speed = speed
        self.imaging_service.Move(request)

    @__ignore_exception
    def move_focus_absolute(self, position, speed=1):
        """
        :param position:
            float in range [0,1]
        :param speed:
            float in range [0,1]
        """
        logger.info(f'Doing move focus absolute')
        request = self.imaging_service.create_type('Move')
        request.VideoSourceToken = self.video_source.token
        request.Focus = self.move_options
        request.Focus.Absolute.Position = position
        request.Focus.Absolute.Speed = speed
        self.imaging_service.Move(request)

    @__ignore_exception
    def stop_focus(self):
        logger.info(f'Stoping focus')
        self.imaging_service.Stop(self.video_source.token)


    def set_preset(self, preset_token=None, preset_name=None):
        """
        :param preset_token:
            unsigned int, usually in range [1, 128] dependent on camera
        :param preset_name:
            string
            if None then duplicate preset_token
        """
        logger.info(f'Setting preset {preset_token} ({preset_name})')
        request = self.ptz_service.create_type('SetPreset')
        request.ProfileToken = self.profile.token
        request.PresetToken = preset_token
        request.PresetName = preset_name
        return self.ptz_service.SetPreset(request)

    def goto_preset(self, preset_token, ptz_velocity=(1.0, 1.0, 1.0)):
        """
        :param preset_token:
            unsigned int
        :param ptz_velocity:
            tuple (pan,tilt,zoom) where
            pan tilt and zoom in range [0,1]
        """
        logger.info(f'Moving to preset {preset_token}, speed={ptz_velocity}')
        ptz_velocity = vector3(*ptz_velocity)
        request = self.ptz_service.create_type('GotoPreset')
        request.ProfileToken = self.profile.token
        request.PresetToken = preset_token
        request.Speed = deepcopy(self.status.Position)
        vel = request.Speed
        vel.PanTilt.x, vel.PanTilt.y = ptz_velocity.x, ptz_velocity.y
        vel.Zoom.x = ptz_velocity.z
        return self.ptz_service.GotoPreset(request)

    def get_presets(self):
        logger.debug(f'Getting presets')
        return self.ptz_service.GetPresets(self.profile.token)

    def move_continuous(self, ptz_velocity, timeout=None):
        """
        :param ptz_velocity:
            tuple (pan,tilt,zoom) where
            pan tilt and zoom in range [-1,1]
        """
        logger.info(f'Continuous move {ptz_velocity} {"" if timeout is None else " for " + str(timeout)}')
        ptz_velocity = vector3(*ptz_velocity)
        req = self.ptz_service.create_type('ContinuousMove')
        req.Velocity = deepcopy(self.status.Position)
        req.ProfileToken = self.profile.token
        vel = req.Velocity
        vel.PanTilt.x, vel.PanTilt.y = ptz_velocity.x, ptz_velocity.y
        vel.Zoom.x = ptz_velocity.z
        # force default space
        vel.PanTilt.space, vel.Zoom.space = None, None
        if timeout is not None:
            if type(timeout) is timedelta:
                req.Timeout = timeout
            else:
                raise TypeError('timeout parameter is of datetime.timedelta type')
        self.ptz_service.ContinuousMove(req)

    def move_absolute(self, ptz_position, ptz_velocity=(1.0, 1.0, 1.0)):
        logger.info(f'Absolute move {ptz_position}')
        ptz_velocity = vector3(*ptz_velocity)
        ptz_position = vector3(*ptz_position)
        req = self.ptz_service.create_type['AbsoluteMove']
        req.ProfileToken = self.profile.token
        pos = req.Position
        pos.PanTilt.x, pos.PanTilt.y = ptz_position.x, ptz_position.y
        pos.Zoom.x = ptz_position.z
        vel = req.Speed
        vel.PanTilt.x, vel.PanTilt.y = ptz_velocity.x, ptz_velocity.y
        vel.Zoom.x = ptz_velocity.z
        self.ptz_service.AbsoluteMove(req)





    def move_relative(self, ptz_position, ptz_velocity=(1.0, 1.0, 1.0)):
        logger.info(f'Relative move {ptz_position}')
        ptz_velocity = vector3(*ptz_velocity)
        ptz_position = vector3(*ptz_position)
        req = self.ptz_service.create_type['RelativeMove']
        req.ProfileToken = self.profile.token
        pos = req.Translation
        pos.PanTilt.x, pos.PanTilt.y = ptz_position.x, ptz_position.y
        pos.Zoom.x = ptz_position.z
        vel = req.Speed
        vel.PanTilt.x, vel.PanTilt.y = ptz_velocity.x, ptz_velocity.y
        vel.Zoom.x = ptz_velocity.z
        self.ptz_service.RelativeMove(req)

    def go_home(self):
        logger.info(f'Moving home')
        req = self.ptz_service.create_type('GotoHomePosition')
        req.ProfileToken = self.profile.token
        self.ptz_service.GotoHomePosition(req)

    def stop(self):
        logger.info(f'Stopping movement')
        self.ptz_service.Stop({'ProfileToken': self.profile.token})

    def __get_move_options(self):
        request = self.imaging_service.create_type('GetMoveOptions')
        request.VideoSourceToken = self.video_source.token
        return self.imaging_service.GetMoveOptions(request)

    def __get_options(self):
        logger.debug(f'Getting options')
        request = self.imaging_service.create_type('GetOptions')
        request.VideoSourceToken = self.video_source.token
        return self.imaging_service.GetOptions(request)

    def __get_video_sources(self):
        logger.debug(f'Getting video source configurations')
        request = self.media_service.create_type('GetVideoSources')
        return self.media_service.GetVideoSources(request)

    def __get_ptz_conf_opts(self):
        logger.debug(f'Getting configuration options')
        request = self.ptz_service.create_type('GetConfigurationOptions')
        request.ConfigurationToken = self.profile.PTZConfiguration.token
        return self.ptz_service.GetConfigurationOptions(request)

    def __get_configurations(self):
        logger.debug(f'Getting configurations')
        request = self.ptz_service.create_type('GetConfigurations')
        return self.ptz_service.GetConfigurations(request)[0]

    def __get_node(self, node_token):
        logger.debug(f'Getting node {node_token}')
        request = self.ptz_service.create_type('GetNode')
        request.NodeToken = node_token
        return self.ptz_service.GetNode(request)

    def __set_imaging_settings(self, imaging_settings):
        logger.debug(f'Setting imaging settings')
        request = self.imaging_service.create_type('SetImagingSettings')
        request.VideoSourceToken = self.video_source.token
        request.ImagingSettings = imaging_settings
        return self.imaging_service.SetImagingSettings(request)

    def __get_imaging_settings(self):
        request = self.im1aging_service.create_type('GetImagingSettings')
        request.VideoSourceToken = self.video_source.token
        return self.imaging_service.GetImagingSettings(request)


