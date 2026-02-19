import numpy as np
import scipy.signal

def convert_to_float32(audio_data):
    """
    Converts raw int16 audio bytes or array to normalized float32.
    """
    if isinstance(audio_data, bytes):
        audio_data = np.frombuffer(audio_data, dtype=np.int16)
    
    return audio_data.astype(np.float32) / 32768.0

def to_mono(audio_float, channels):
    """
    Mixes stereo audio to mono if necessary.
    """
    if channels > 1:
        # Reshape to (Frames, Channels)
        if len(audio_float) % channels == 0:
            audio_float = audio_float.reshape(-1, channels)
            audio_float = audio_float.mean(axis=1)
    return audio_float

def resample_audio(audio_float, original_rate, target_rate=16000):
    """
    Resamples audio to target sample rate using scipy.signal.resample.
    Note: scipy.signal.resample assumes the input is the entire signal (Fourier method).
    For streaming, polyphase resampling (resample_poly) is often better, 
    but for fixed chunks 'resample' is usually fine and fast.
    """
    if original_rate != target_rate:
        num_samples = int(len(audio_float) * target_rate / original_rate)
        audio_float = scipy.signal.resample(audio_float, num_samples)
    return audio_float

def is_speech(audio_float, threshold=0.001):
    """
    Simple energy-based Voice Activity Detection (VAD).
    Returns (True, rms) if the RMS amplitude of the audio chunk exceeds the threshold.
    """
    rms = np.sqrt(np.mean(audio_float**2))
    return rms > threshold, rms
