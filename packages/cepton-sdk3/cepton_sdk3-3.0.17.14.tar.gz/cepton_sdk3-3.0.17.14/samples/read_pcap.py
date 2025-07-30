#!/usr/bin/env python3
"""
Sample script for getting points from a pcap.
"""
import argparse

import cepton_sdk3.utils as utils

parser = argparse.ArgumentParser()
parser.add_argument(
    "-f", "--file", type=str, required=True, help="Input pcap path to parse."
)

if __name__ == "__main__":
    args = parser.parse_args()
    capture_path = args.file

    print("Read", capture_path)
    FRAME_COUNT = 0
    for frame in utils.read_pcap(capture_path):
        FRAME_COUNT += 1
        print(
            f"get frame: {FRAME_COUNT}, size: {len(frame.flags)}, handle: {frame.handle[0]} start timestamp: {frame.timestamps[0]*1e-6:.6f}s duration: {(frame.timestamps[-1] - frame.timestamps[0])*1e-6:.6f}s"
        )
