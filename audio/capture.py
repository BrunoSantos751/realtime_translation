import pyaudiowpatch as pyaudio
import time
import wave
import os
import datetime

class AudioCapture:
    def __init__(self):
        self.p = pyaudio.PyAudio()
        self.loopback_device = None

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
            for i in range(wasapi_info["deviceCount"]):
                dev = self.p.get_device_info_by_host_api_device_index(wasapi_info["index"], i)
                if dev["index"] == default_output_device:
                    # Found the default output, now look for its loopback
                    # In pyaudiowpatch, loopback devices are often separate or accessible via a flag
                    # But typically we want to open the *output* device in loopback mode.
                    # Wait, pyaudiowpatch creates a specific "Loopback" device for each output.
                    pass

            # Search specifically for the loopback of the default output
            for loopback in self.p.get_loopback_device_info_generator():
                if loopback["isLoopbackDevice"]:
                     # This is a candidate. ideally we match it to the system default.
                     return loopback
                     
            return None
        except OSError as e:
            print(f"Error finding loopback device: {e}")
            return None

    def capture_loopback_chunks(self, chunk_duration=1.0, sample_rate=44100):
        """
        Captures audio from the default loopback device in chunks.
        Yields raw audio data.
        """
        # Get default WASAPI speakers
        try:
            wasapi_info = self.p.get_host_api_info_by_type(pyaudio.paWASAPI)
        except OSError:
            print("WASAPI not found. Make sure you are on Windows.")
            return

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

        if not loopback_device:
            print("Default loopback device not found.")
            return

        print(f"Recording from: {loopback_device['name']} ({loopback_device['index']})")
        
        self.loopback_device = loopback_device

        # CHUNK size for processing (not the 1s chunk)
        FRAME_COUNT = int(loopback_device["defaultSampleRate"] * chunk_duration)
        
        try:
            stream = self.p.open(format=pyaudio.paInt16,
                                 channels=loopback_device["maxInputChannels"],
                                 rate=int(loopback_device["defaultSampleRate"]),
                                 input=True,
                                 input_device_index=loopback_device["index"],
                                 frames_per_buffer=FRAME_COUNT)
        except Exception as e:
            print(f"Failed to open stream: {e}")
            return

        
        print("Stream started.")
        
        try:
            while True:
                data = stream.read(FRAME_COUNT)
                yield data, int(loopback_device["defaultSampleRate"]), loopback_device["maxInputChannels"]
        except KeyboardInterrupt:
            pass
        finally:
            stream.stop_stream()
            stream.close()

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
        print(f"Saved: {filename}")
        return filename

    def close(self):
        self.p.terminate()


