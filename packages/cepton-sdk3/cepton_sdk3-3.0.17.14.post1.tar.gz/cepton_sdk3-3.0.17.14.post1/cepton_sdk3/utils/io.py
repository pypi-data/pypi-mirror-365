"""IO Utilities"""

from .. import sdk


def read_pcap(path: str, frame_mode: int = 0):
    """Returns an iterator over frame sin a pcap"""
    capture_path = path

    # Initialize
    sdk.initialize()

    # LoadPcap
    # speed=100 means 1x speed. Speed=0 means as fast as possible.
    sdk.load_pcap(capture_path, speed=100, pause_on_load=True)

    # Enable FIFO feature
    # Frame aggregation mode set to 0(natrual). Allocate 400 frame buffers in the frame FIFO
    sdk.enable_frame_fifo(frame_mode=frame_mode, num_frames=400)
    sdk.replay_play()

    # Loop until pcap replay is finished
    while not sdk.replay_is_finished():
        frame = sdk.frame_fifo_get_frame(timeout=2000)  # 2000 ms
        if not frame is None:
            yield frame

    # Disable FIFO feature
    sdk.disable_frame_fifo()
    # Deinitialize
    sdk.deinitialize()
