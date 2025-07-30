# Raw C interface through the CDLL library
import os
import sys
import platform
import ctypes


def c_struct_to_dict(c_obj, excludes):
    """Converts ctypes tructure to a dict"""
    data = {}
    for field in c_obj._fields_:
        name = field[0]
        if not name:
            continue
        if name in excludes:
            continue
        data[name] = getattr(c_obj, name)
    return data


# Supported platform-machine combinations
#  win32-x64
#  linux-x64, linux-arm64 (NVIDIA Jetson)
#  darwin-x64, darwin-arm64
__machine_lookup = {
    "AMD64": "x64",
    "x86_64": "x64",
    "aarch64": "arm64",
}

__platform_lookup = {
    "win32": "win",
}


def _load_sdk():
    name = "cepton_sdk3"

    # Find platform
    mach = platform.machine()
    if mach in __machine_lookup:
        mach = __machine_lookup[mach]
    # Find arch
    pl = sys.platform
    if pl in __platform_lookup:
        pl = __platform_lookup[pl]

    if pl == "linux":
        lib_name = f"lib{name}.so"
    elif pl == "darwin":
        lib_name = f"lib{name}.dylib"
    elif pl == "win" or pl == "win32":
        lib_name = f"{name}.dll"
    else:
        raise NotImplementedError("Platform not supported!")
    lib_dir = f"lib/{pl}-{mach}/"

    # Try local and global search paths
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(parent_dir, lib_dir, lib_name)
    if not os.path.exists(path):
        path = lib_name
    print("LOADING ", path)
    return ctypes.CDLL(path)


# =====================
# Refer to cepton_sdk2.h
#
CEPTON_API_VERSION = 205

lib = _load_sdk()

GetErrorCodeName = lib.CeptonGetErrorCodeName
GetErrorCodeName.restype = ctypes.c_char_p

GetSdkVersion = lib.CeptonGetSdkVersion

SensorHandle = ctypes.c_uint64

SensorErrorCallback = ctypes.CFUNCTYPE(
    None, SensorHandle, ctypes.c_int, ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t
)

Initialize = lib.CeptonInitialize
Deinitialize = lib.CeptonDeinitialize
StartNetworking = lib.CeptonStartNetworking
StartNetworkingOnPort = lib.CeptonStartNetworkingOnPort
StartNetworkingMulticast = lib.CeptonStartNetworkingMulticast
StartNetworkingMulticast.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint16]
StopNetworking = lib.CeptonStopNetworking

ReplayHandle = ctypes.c_void_p

ReplayLoadPcap = lib.CeptonReplayLoadPcap
ReplayLoadPcap.argtypes = [ctypes.c_char_p, ctypes.c_int, ctypes.POINTER(ReplayHandle)]

ReplayUnloadPcap = lib.CeptonReplayUnloadPcap
ReplayPlay = lib.CeptonReplayPlay
ReplayPlayToFinish = lib.CeptonReplayPlayToFinish
ReplayPause = lib.CeptonReplayPause
ReplayGetLength = lib.CeptonReplayGetLength
ReplaySeek = lib.CeptonReplaySeek
ReplayGetSeekPosition = lib.CeptonReplayGetSeekPosition
ReplayNextFrame = lib.CeptonReplayNextFrame
ReplaySetSpeed = lib.CeptonReplaySetSpeed
ReplayGetSpeed = lib.CeptonReplayGetSpeed
ReplayGetIndexPosition = lib.CeptonReplayGetIndexPosition
ReplayIsFinished = lib.CeptonReplayIsFinished
ReplayIsPaused = lib.CeptonReplayIsPaused


class SDKFrameArray(ctypes.Structure):
    """Structure of arrays representing an SDK frame.
    Corresponds to `CeptonFrameExDataArray` in the SDK"""

    _fields_ = [
        ("x", ctypes.POINTER(ctypes.c_int32)),
        ("y", ctypes.POINTER(ctypes.c_int32)),
        ("z", ctypes.POINTER(ctypes.c_int32)),
        ("reflectivities", ctypes.POINTER(ctypes.c_uint16)),
        ("timestamps", ctypes.POINTER(ctypes.c_int64)),
        ("channel_ids", ctypes.POINTER(ctypes.c_uint16)),
        ("flags", ctypes.POINTER(ctypes.c_uint16)),
        ("handle", ctypes.POINTER(SensorHandle)),
    ]


class SdkSensor(ctypes.Structure):
    """Struct representing sensor data"""

    _fields_ = [
        ("info_size", ctypes.c_uint32),
        ("serial_number", ctypes.c_uint32),
        ("handle", SensorHandle),
        ("model_name", ctypes.c_char * 28),
        ("model", ctypes.c_uint16),
        ("", ctypes.c_uint16),  # model_reserved
        ("part_number", ctypes.c_uint32),
        ("firmware_version", ctypes.c_uint32),
        ("power_up_timestamp", ctypes.c_int64),
        ("time_sync_offset", ctypes.c_int64),
        ("time_sync_drift", ctypes.c_int64),
        ("return_count", ctypes.c_uint8),
        ("channel_count", ctypes.c_uint8),
        ("", ctypes.c_uint8 * 2),
        ("status_flags", ctypes.c_uint32),
    ]

    def to_dict(self):
        """Convert info to dict"""
        d = c_struct_to_dict(self, ["info_size", "model_name", "status_flags"])
        d["model_name"] = self.model_name.decode("utf8")
        # Add status flags
        # CEPTON_SENSOR_PTP_CONNECTED = 1,
        # CEPTON_SENSOR_PPS_CONNECTED = 2,
        # CEPTON_SENSOR_NMEA_CONNECTED = 4,
        fl = self.status_flags
        d["status_ptp_connected"] = (fl & 1) != 0
        d["status_pps_connected"] = (fl & 2) != 0
        d["status_nmea_connected"] = (fl & 4) != 0
        return d


GetSensorCount = lib.CeptonGetSensorCount
GetSensorInformationByIndex = lib.CeptonGetSensorInformationByIndex
GetSensorInformation = lib.CeptonGetSensorInformation

EnableFrameFifoEx = lib.CeptonEnableFrameFifoEx
EnableFrameFifoEx.argtypes = [ctypes.c_int32, ctypes.c_uint32]
DisableFrameFifoEx = lib.CeptonDisableFrameFifoEx

FrameFifoExNext = lib.CeptonFrameFifoExNext
FrameFifoExIsEmpty = lib.CeptonFrameFifoExEmpty
FrameFifoExIsFull = lib.CeptonFrameFifoExFull

FrameFifoExFillArray = lib.CeptonFrameFifoExFillArray
FrameFifoExFillArray.argtypes = [ctypes.POINTER(SDKFrameArray), ctypes.c_uint32]

FrameFifoExPeekNumPoints = lib.CeptonFrameFifoExPeekFrameNumPoints
FrameFifoExPeekNumPoints.argtypes = [ctypes.c_uint32]


SensorInfoCallback = ctypes.CFUNCTYPE(
    None, SensorHandle, ctypes.POINTER(SdkSensor), ctypes.c_void_p
)
ListenSensorInfo = lib.CeptonListenSensorInfo
UnlistenSensorInfo = lib.CeptonUnlistenSensorInfo


# Service for sdk.py
byref = ctypes.byref
