from audio.capture import AudioCapture
import time
from speech.whisper_engine import WhisperTranscriber

from audio.preprocess import convert_to_float32, to_mono, resample_audio, is_speech

def main():
    capturer = AudioCapture()
    try:
        print("Listing valid loopback devices:")
        # Just listing for demonstration
        devices = capturer.list_devices()
        
        print("\nStarting capture (Press Ctrl+C to stop)...")
    
        # Initialize Transcriber
        transcriber = WhisperTranscriber(model_name="base") # tiny, base, small, medium, large
        
        capturer.start_capture(chunk_duration=2.5) 
        while True:
            # Use the new method to get the latest chunk and clear backlog
            chunk_data, dropped_count = capturer.get_last_chunk_and_clear()
            
            if dropped_count > 0:
                print(f"\n[Warning] High latency detected! Dropped {dropped_count} old audio chunks to catch up.")

            if chunk_data:
                data, timestamp, rate, channels = chunk_data
                
                # Calculate latency
                current_time = time.time()
                capture_latency_ms = (current_time - timestamp) * 1000
                
                # Preprocessing
                audio_float = convert_to_float32(data)
                audio_mono = to_mono(audio_float, channels)
                
                # VAD Check (Skip silence)
                # Lower limit to 0.005 to catch softer audio
                speech_detected, rms_val = is_speech(audio_mono, threshold=0.001)
                
                if not speech_detected:
                    print(f".{rms_val:.4f} ", end="", flush=True) 
                    continue
                
                audio_resampled = resample_audio(audio_mono, rate, 16000)

                # Transcribe
                # Language can be "pt", "en", etc. or None for auto-detection
                text, processing_time_ms = transcriber.transcribe(audio_resampled, language="pt")
                
                if text:
                    print(f"[{processing_time_ms:.0f}ms] {text} (Latency: {capture_latency_ms:.0f}ms)")
                else:
                    print(f".", end="", flush=True) # visual feedback for silence/no text
                
                # Save chunk (optional, can comment out to avoid disk spam)
                # capturer.save_chunk_to_wav(data, rate, channels)
            
            # Sleep briefly to avoid busy loop if buffer is empty, 
            # but short enough to consume quickly
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping capture...")
    finally:
        capturer.close()

if __name__ == "__main__":
    main()