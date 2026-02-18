from audio.capture import AudioCapture
import time

def main():
    capturer = AudioCapture()
    try:
        print("Listing valid loopback devices:")
        # Just listing for demonstration
        devices = capturer.list_devices()
        
        print("\nStarting capture (Press Ctrl+C to stop)...")
        capturer.start_capture(chunk_duration=0.3)
        while True:
            chunk_data = capturer.get_latest_chunk()
            if chunk_data:
                data, timestamp, rate, channels = chunk_data
                
                # Calculate latency
                current_time = time.time()
                latency_ms = (current_time - timestamp) * 1000
                
                print(f"Captured chunk. Latency: {latency_ms:.2f} ms")
                
                # Verify no freezing by printing a dot or similar interaction if needed
                # Here we strictly follow the plan to print latency
                
                # Save chunk (optional, can comment out to avoid disk spam)
                capturer.save_chunk_to_wav(data, rate, channels)
            
            # Sleep briefly to avoid busy loop if buffer is empty, 
            # but short enough to consume quickly
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping capture...")
    finally:
        capturer.close()

if __name__ == "__main__":
    main()