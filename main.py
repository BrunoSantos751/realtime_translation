from audio.capture import AudioCapture
import time

def main():
    capturer = AudioCapture()
    try:
        print("Listing valid loopback devices:")
        # Just listing for demonstration
        devices = capturer.list_devices()
        
        print("\nStarting capture (Press Ctrl+C to stop)...")
        # In a real app, this would likely be threaded or part of a pipeline
        for data, rate, channels in capturer.capture_loopback_chunks(chunk_duration=1.0):
            # Here you would pass 'data' to the translation pipeline
            # For now, we just save it
            file_path = capturer.save_chunk_to_wav(data, rate, channels)
            # print(f"Captured chunk: {file_path}")
            
    except KeyboardInterrupt:
        print("\nStopping capture...")
    finally:
        capturer.close()

if __name__ == "__main__":
    main()