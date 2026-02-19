
import numpy as np
import scipy.signal
import time

def test_speed():
    # Simulate 2.5s of audio at 48kHz (120,000 samples)
    duration = 2.5
    original_rate = 48000
    target_rate = 16000
    channels = 2
    
    # Create random audio data (float32, mono for resampling)
    # usually capture is stereo, then converted to mono. 
    # Let's assume input to resample is mono float32 array.
    num_samples = int(duration * original_rate)
    audio_data = np.random.uniform(-1.0, 1.0, num_samples).astype(np.float32)

    print(f"Testing resampling 2.5s of audio ({num_samples} samples) from {original_rate}Hz to {target_rate}Hz")

    # Method 1: scipy.signal.resample (FFT based)
    start_time = time.time()
    for _ in range(10):
        target_samples = int(len(audio_data) * target_rate / original_rate)
        scipy.signal.resample(audio_data, target_samples)
    end_time = time.time()
    print(f"scipy.signal.resample average time: {(end_time - start_time) * 100:.2f}ms")

    # Method 2: scipy.signal.resample_poly (Polyphase)
    # up = target_rate, down = original_rate. simplify fraction
    import math
    gcd = math.gcd(target_rate, original_rate)
    up = target_rate // gcd
    down = original_rate // gcd
    
    start_time = time.time()
    for _ in range(10):
        scipy.signal.resample_poly(audio_data, up, down)
    end_time = time.time()
    print(f"scipy.signal.resample_poly average time: {(end_time - start_time) * 100:.2f}ms")

if __name__ == "__main__":
    test_speed()
