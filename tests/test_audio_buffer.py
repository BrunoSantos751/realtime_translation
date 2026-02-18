import unittest
import time
import collections
import sys
import os

# Add the project root to sys.path so we can import audio.capture
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from audio.capture import AudioCapture

class TestAudioBuffer(unittest.TestCase):
    def test_buffer_initialization(self):
        capture = AudioCapture(buffer_size=10)
        self.assertIsInstance(capture.audio_queue, collections.deque)
        self.assertEqual(capture.audio_queue.maxlen, 10)

    def test_buffer_overflow_behavior(self):
        # Test that deque behaves as a circular buffer
        capture = AudioCapture(buffer_size=3)
        for i in range(5):
            capture.audio_queue.append(i)
        
        self.assertEqual(len(capture.audio_queue), 3)
        self.assertEqual(list(capture.audio_queue), [2, 3, 4]) # Oldest (0, 1) dropped

    def test_latency_calculation(self):
        # Simulate a captured chunk
        capture = AudioCapture()
        timestamp = time.time() - 0.1 # 100ms ago
        capture.audio_queue.append((b'data', timestamp, 44100, 2))
        
        chunk = capture.get_latest_chunk()
        self.assertIsNotNone(chunk)
        
        data, ts, rate, channels = chunk
        latency = time.time() - ts
        self.assertTrue(latency >= 0.1)

if __name__ == '__main__':
    unittest.main()
