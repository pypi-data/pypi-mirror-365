#!/usr/bin/env python3

import unittest

import cepton_sdk3 as sdk


class BasicTests(unittest.TestCase):
    """Basic tests"""

    def test_initialize(self):
        """Test initialize and deinitialize"""
        sdk.initialize()
        sdk.deinitialize()

    def test_replay(self):
        """Test that replay works"""
        sdk.initialize()
        sdk.enable_frame_fifo(0, 10)
        sdk.load_pcap("/root/Documents/cepton/lobby-1.pcap")

        frame_counts = []
        for _ in range(10):
            frame = sdk.frame_fifo_get_frame(2000)
            frame_counts.append(frame.positions.shape[0])

        self.assertGreater(len(frame_counts), 0)
        self.assertTrue(all(count > 0 for count in frame_counts))

        sdk.deinitialize()
