import numpy as np

from .soa import StructureOfArrays

# SDK position units -> meters conversion
UNITS_TO_METERS = 1.0 / 65536.0


class Frame(StructureOfArrays):
    """3D points array.

    Attributes:
        timestamps
        x_raw
        y_raw
        z_raw
        positions (N*3)
        reflectivities
        reflectivities_raw
        channel_ids
        invalid
        saturated
        handle
    """

    def __init__(self, n=0):
        super().__init__(n)
        self.timestamps = np.zeros([n], dtype=np.int64)
        self.x_raw = np.zeros([n], dtype=np.int32)
        self.y_raw = np.zeros([n], dtype=np.int32)
        self.z_raw = np.zeros([n], dtype=np.int32)
        self.positions = np.zeros([n, 3], dtype=np.float32)
        self.reflectivities = np.zeros([n], dtype=np.float32)
        self.reflectivities_raw = np.zeros([n], dtype=np.uint16)
        self.channel_ids = np.zeros([n], dtype=np.uint16)
        self.flags = np.zeros([n], dtype=np.uint16)
        self.saturated = np.zeros([n], dtype=bool)
        self.blooming = np.zeros([n], dtype=bool)
        self.frame_parity = np.zeros([n], dtype=bool)
        self.frame_boundary = np.zeros([n], dtype=bool)
        self.second_return = np.zeros([n], dtype=bool)
        self.invalid = np.zeros([n], dtype=bool)
        self.noise = np.zeros([n], dtype=bool)
        self.blocked = np.zeros([n], dtype=bool)
        self.handle = np.zeros([1], dtype=np.uint64)

    def _finalize(self):
        CEPTON_POINT_SATURATED = 1 << 0
        CEPTON_POINT_BLOOMING = 1 << 1
        CEPTON_POINT_FRAME_PARITY = 1 << 2
        CEPTON_POINT_FRAME_BOUNDARY = 1 << 3
        CEPTON_POINT_SECOND_RETURN = 1 << 4
        CEPTON_POINT_NO_RETURN = 1 << 5
        CEPTON_POINT_NOISE = 1 << 6
        CEPTON_POINT_BLOCKED = 1 << 7

        np.multiply(
            np.stack([self.x_raw, self.y_raw, self.z_raw], 1),
            UNITS_TO_METERS,
            out=self.positions,
        )
        self.reflectivities[:] = self.reflectivities_raw
        self.saturated[:] = np.bitwise_and(self.flags, CEPTON_POINT_SATURATED) != 0
        self.blooming[:] = np.bitwise_and(self.flags, CEPTON_POINT_BLOOMING) != 0
        self.frame_parity[:] = (
            np.bitwise_and(self.flags, CEPTON_POINT_FRAME_PARITY) != 0
        )
        self.frame_boundary[:] = (
            np.bitwise_and(self.flags, CEPTON_POINT_FRAME_BOUNDARY) != 0
        )
        self.second_return[:] = (
            np.bitwise_and(self.flags, CEPTON_POINT_SECOND_RETURN) != 0
        )
        self.invalid[:] = np.bitwise_and(self.flags, CEPTON_POINT_NO_RETURN) != 0
        self.noise[:] = np.bitwise_and(self.flags, CEPTON_POINT_NOISE) != 0
        self.blocked[:] = np.bitwise_and(self.flags, CEPTON_POINT_BLOCKED) != 0

    @classmethod
    def _get_array_member_names(cls):
        return [
            "timestamps",
            "x_raw",
            "y_raw",
            "z_raw",
            "positions",
            "reflectivities",
            "reflectivities_raw",
            "channel_ids",
            "flags",
            "saturated",
            "blooming",
            "frame_parity",
            "frame_boundary",
            "second_return",
            "invalid",
            "noise",
            "blocked",
            "handle",
        ]
