import pyaudiowpatch as pyaudio
import time
import wave
import os
import datetime
import threading
import collections
import queue

class AudioCapture:
    def __init__(self, buffer_size=50):
        self.p = pyaudio.PyAudio()
        self.loopback_device = None
        self.recording = False
        self.thread = None
        # Circular buffer using deque with maxlen
        # Stores tuples: (audio_data, timestamp, sample_rate, channels)
        self.audio_queue = collections.deque(maxlen=buffer_size) 
        self.chunk_duration = 0.3 # Default chunk duration

    def list_devices(self):
        """Lists all available audio devices and returns a list of dictionaries."""
        print("Searching for devices...")
        info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
        num_devices = info.get('deviceCount')
        devices = []
        
        for i in range(0, num_devices):
            device_info = self.p.get_device_info_by_host_api_device_index(info["index"], i)
            if device_info.get("maxInputChannels") > 0:
                 # In WASAPI, loopback devices are input devices
                 pass
            
            # Print all for debugging
            print(f"Device {i}: {device_info.get('name')} - Loopback: {device_info.get('isLoopbackDevice')}")
            devices.append(device_info)
            
        return devices

    def get_default_loopback_device(self):
        """Finds the default WASAPI loopback device."""
        try:
            # Get default WASAPI output device
            wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
            default_output_device = wasapi_info["defaultOutputDevice"]
            
            # Find the corresponding loopback device
            # Search specifically for the loopback of the default output
            for loopback in self.p.get_loopback_device_info_generator():
                if loopback["isLoopbackDevice"]:
                     # This is a candidate. ideally we match it to the system default.
                     if loopback["index"] == default_output_device: # This check might need refinement based on specific hardware
                         return loopback
            
            # Fallback: Just return the first loopback device found if strict matching fails or is complex
            for loopback in self.p.get_loopback_device_info_generator():
                 if loopback["isLoopbackDevice"]:
                    return loopback
                     
            return None
        except OSError as e:
            print(f"Error finding loopback device: {e}")
            return None

    def _find_loopback_device(self):
        # reuse the logic from get_default_loopback_device or similar logic
         # Get default WASAPI speakers
        try:
            wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            print("WASAPI not found. Make sure you are on Windows.")
            return None

        # Get default output device info
        default_output = self.p.get_device_info_by_index(wasapi_info["defaultOutputDevice"])
        default_output_name = default_output["name"]
        print(f"Default Output Device: {default_output_name}")

        # Find the loopback device that matches the default output device
        loopback_device = None
        for i in range(self.p.get_device_count()):
            dev = self.p.get_device_info_by_index(i)
            if dev.get("isLoopbackDevice") and dev["hostApi"] == wasapi_info["index"]:
                # Check if the name matches (pyaudiowpatch usually appends [Loopback])
                if default_output_name in dev["name"]:
                    loopback_device = dev
                    break
        
        # Fallback: if no name match, pick the first loopback device found
        if not loopback_device:
            print("Could not find exact name match for loopback, searching for any loopback...")
            for i in range(self.p.get_device_count()):
                dev = self.p.get_device_info_by_index(i)
                if dev.get("isLoopbackDevice") and dev["hostApi"] == wasapi_info["index"]:
                    loopback_device = dev
                    break
        return loopback_device

    def start_capture(self, chunk_duration=1.0):
        """Starts the audio capture in a background thread."""
        if self.recording:
            print("Already recording.")
            return

        self.chunk_duration = chunk_duration
        self.loopback_device = self._find_loopback_device()
        
        if not self.loopback_device:
            print("No loopback device found.")
            return

        self.recording = True
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()
        print(f"Started background capture from {self.loopback_device['name']}")

    def stop_capture(self):
        """Stops the background capture thread."""
        self.recording = False
        if self.thread and self.thread.is_alive():
            self.thread.join()
        print("Capture stopped.")

    def _capture_loop(self):
        """Internal method to capture audio continuously."""
        # Calculate frame count for the desired chunk duration
        FRAME_COUNT = int(self.loopback_device["defaultSampleRate"] * self.chunk_duration)
        
        try:
            stream = self.p.open(format=pyaudio.paInt16,
                                 channels=self.loopback_device["maxInputChannels"],
                                 rate=int(self.loopback_device["defaultSampleRate"]),
                                 input=True,
                                 input_device_index=self.loopback_device["index"],
                                 frames_per_buffer=FRAME_COUNT)
        except Exception as e:
            print(f"Failed to open stream: {e}")
            self.recording = False
            return

        print("Stream opened in background thread.")
        
        while self.recording:
            try:
                # Blocking read
                data = stream.read(FRAME_COUNT, exception_on_overflow=False)
                timestamp = time.time()
                
                # Add to circular buffer
                # (data, timestamp, sample_rate, channels)
                self.audio_queue.append((
                    data, 
                    timestamp, 
                    int(self.loopback_device["defaultSampleRate"]), 
                    self.loopback_device["maxInputChannels"]
                ))
                
            except Exception as e:
                print(f"Error during capture: {e}")
                break
        
        stream.stop_stream()
        stream.close()

    def get_latest_chunk(self):
        """
        Retrieves the oldest chunk from the buffer (FIFO).
        Returns None if buffer is empty.
        """
        try:
            return self.audio_queue.popleft()
        except IndexError:
            return None

    def get_last_chunk_and_clear(self):
        """
        Retrieves the *newest* chunk from the buffer and clears the rest.
        Returns (chunk, dropped_count).
        If buffer is empty, returns (None, 0).
        """
        if not self.audio_queue:
            return None, 0
            
        dropped = len(self.audio_queue) - 1
        # Get the last item (newest)
        item = self.audio_queue[-1] 
        # Clear the queue
        self.audio_queue.clear()
        
        return item, dropped

    def save_chunk_to_wav(self, data, sample_rate, channels, output_dir="recordings"):
        """Saves a chunk of audio data to a WAV file."""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        filename = os.path.join(output_dir, f"chunk_{timestamp}.wav")
        
        wf = wave.open(filename, 'wb')
        wf.setnchannels(channels)
        wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(sample_rate)
        wf.writeframes(data)
        wf.close()
        # print(f"Saved: {filename}")
        return filename

    def close(self):
        self.stop_capture()
        self.p.terminate()