"""Simple example to plot a couple frames"""

import os
import argparse
import matplotlib.pyplot as plt

import cepton_sdk3 as sdk
import cepton_sdk3.utils as utils

parser = argparse.ArgumentParser()
parser.add_argument("pcap", help="Pcap file to input")
args = parser.parse_args()

os.makedirs("data", exist_ok=True)


try:
    for i, frame in enumerate(utils.read_pcap(args.pcap)):
        if i > 5:
            break

        fig = plt.figure()
        ax = fig.subplots(1, 1)
        ax.scatter(
            frame.positions[:, 0] / frame.positions[:, 1],
            frame.positions[:, 2] / frame.positions[:, 1],
            s=0.1,
            c=frame.reflectivities,
        )
        fig.savefig(f"data/frame_{i}.jpg")
finally:
    sdk.deinitialize()
