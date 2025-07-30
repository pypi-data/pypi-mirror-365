import ctypes
from . import c as _c
from .sensor import Sensor
from .frame import Frame


# SDK singleton management object, holds private module variables
# pylint: disable=C0103,R0903
class __Sdk:
    cbFrame = None
    cbSensor = None

    # TODO: better handle replay handles
    replayHandle = _c.ReplayHandle()

    @staticmethod
    def error_cb():
        """Error callback"""
        return


class CeptonError(Exception):
    """Cepton Error Code"""

    def __init__(self, code=0):
        self.code_name = get_error_code_name(code)
        super().__init__(self.code_name)
        self.code = code


def __check(code):
    if code < 0:
        raise CeptonError(code)


def _sensor_cb(handle, sensor_ptr, user_data):
    d = sensor_ptr[0].to_dict()

    s = Sensor.find_or_create_by_handle(handle)
    s.update_info(d)


def initialize():
    """Initialize the SDK"""
    fn = _c.SensorErrorCallback(__Sdk.error_cb)
    __check(_c.Initialize(_c.CEPTON_API_VERSION, fn))
    __Sdk.cbSensor = _c.SensorInfoCallback(_sensor_cb)
    __check(_c.ListenSensorInfo(__Sdk.cbSensor, None))


def deinitialize():
    """Deinitialize the SDK"""
    __check(_c.UnlistenSensorInfo(__Sdk.cbSensor, None))
    __Sdk.cbSensor = None
    __check(_c.Deinitialize())


def get_error_code_name(err: int) -> str:
    """Get the error name corresponding to a specific error code"""
    return _c.GetErrorCodeName(err).decode("utf8")


def get_version() -> str:
    """
    Returns a 3-part or 4-part version string like 2.0.10 or 2.0.10.1
    Only returns 4-part if the last part is non-zero
    """
    v = _c.GetSdkVersion()
    v0 = v & 0xFF
    v1 = (v >> 8) & 0xFF
    v2 = (v >> 16) & 0xFF
    v3 = v >> 24
    vs = f"{v0}.{v1}.{v2}"
    if v3 != 0:
        vs += f".{v3}"
    return vs


def get_sensor_information_by_index(ind):
    """Get sensor information by index"""
    info = _c.SdkSensor()
    _c.GetSensorInformationByIndex(ind, _c.byref(info))
    return info.to_dict()


def get_sensor_information_by_handle(handle):
    """Get sensor information by handle"""
    info = _c.SdkSensor()
    _c.GetSensorInformation(handle, _c.byref(info))
    return info.to_dict()


def load_pcap(pcap: str, **kwargs):
    """Load one pcap
    LoadPcap(pcap, looping=false, speed=100)
    """
    # CEPTON_REPLAY_FLAG_LOAD_WITHOUT_INDEX = 1,
    # CEPTON_REPLAY_FLAG_PLAY_LOOPED = 2,
    # CEPTON_REPLAY_FLAG_LOAD_PAUSED = 4,
    flags = 0  # by default the pcap replays automatically and does not loop.
    speed = kwargs.get("speed", 100)
    if kwargs.get("looping", False):
        flags |= 2  # looping
    if kwargs.get("pause_on_load", False):
        flags |= 4  # paused on load
    # TODO: Check kwargs for bad parameters

    # Start of the actual actions
    __check(_c.ReplayLoadPcap(pcap.encode("utf8"), flags, _c.byref(__Sdk.replayHandle)))
    if speed != 100:
        __check(_c.ReplaySetSpeed(__Sdk.replayHandle, speed))


def replay_play():
    """Start or resume playing of the current pcap handle"""
    __check(_c.ReplayPlay(__Sdk.replayHandle))


def replay_is_finished():
    """Check whether the replay is finished"""
    return _c.ReplayIsFinished(__Sdk.replayHandle)


def unload_pcap():
    """Unload the pcap"""
    if __Sdk.replayHandle:
        __check(_c.ReplayUnloadPcap(__Sdk.replayHandle))


def start_networking():
    """
    Start listening to sensor network.
    """
    __check(_c.StartNetworking())


def start_networking_multicast(target_mcast_group, local_interface, port):
    """Start multicast networking"""
    __check(_c.StartNetworkingMulticast(target_mcast_group, local_interface, port))


def stop_networking():
    """
    Stop listening to sensor network.
    """
    __check(_c.StopNetworking())


def enable_frame_fifo(frame_mode, num_frames):
    """
    Enable SDK frame FIFO feature.

    Parameters
    ----------
    frame_mode : int
        = 0 for natural frame aggregation.
        > 0 for fixed time period in millisecond.
    num_frames : int
        Maximum number of frames in the FIFO.
    """
    assert 0 <= frame_mode

    # Convert to us convention in Cepton SDK
    __check(_c.EnableFrameFifoEx(frame_mode * 1000, num_frames))


def disable_frame_fifo():
    """Disable the frame fifo"""
    __check(_c.DisableFrameFifoEx())


def frame_fifo_get_frame(timeout):
    """
    Get a cepton_sdk3.Frame instance from the frame FIFO.

    This progresses the FIFO.

    Parameters
    ----------
    timeout : int
        Maximum time spend on waiting for the next frame. 0 represents
        wait forever. Larger than 0 represents maximum wait time in
        millisencond. Function will return a None if timeout.

    Return
    ----------
    A cepton_sdk3.Frame instance or None.
    """
    try:
        length = _c.FrameFifoExPeekNumPoints(2000)
        __check(length)
        # initialize to zeros
        frame = Frame(length)
        sdk_frame = _c.SDKFrameArray()
        sdk_frame.x = frame.x_raw.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        sdk_frame.y = frame.y_raw.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        sdk_frame.z = frame.z_raw.ctypes.data_as(ctypes.POINTER(ctypes.c_int32))
        sdk_frame.reflectivities = frame.reflectivities_raw.ctypes.data_as(
            ctypes.POINTER(ctypes.c_uint16)
        )
        sdk_frame.timestamps = frame.timestamps.ctypes.data_as(
            ctypes.POINTER(ctypes.c_int64)
        )
        sdk_frame.channel_ids = frame.channel_ids.ctypes.data_as(
            ctypes.POINTER(ctypes.c_uint16)
        )
        sdk_frame.flags = frame.flags.ctypes.data_as(ctypes.POINTER(ctypes.c_uint16))
        sdk_frame.handle = frame.handle.ctypes.data_as(ctypes.POINTER(ctypes.c_uint64))
        __check(_c.FrameFifoExFillArray(_c.ctypes.byref(sdk_frame), timeout))
        __check(_c.FrameFifoExNext())
    except CeptonError as e:
        if e.code_name == "CEPTON_ERROR_TIMEOUT":
            return None
        else:
            raise
    # pylint: disable=W0212
    frame._finalize()
    return frame
