from audio.capture import AudioCapture
import time
from speech.whisper_engine import WhisperTranscriber

from audio.preprocess import convert_to_float32, to_mono, resample_audio, is_speech
from pipeline.rolling_buffer import RollingAudioBuffer

def main():
    capturer = AudioCapture()
    try:
        print("Listing valid loopback devices:")
        # Just listing for demonstration
        devices = capturer.list_devices()
        
        print("\nStarting capture (Press Ctrl+C to stop)...")
    
        # Initialize Transcriber
        transcriber = WhisperTranscriber(model_name="small") # tiny, base, small, medium, large
        
        from translation.translator import TranslationEngine
        translator = TranslationEngine()
        
        # Inicia o rolling buffer (janela: 2.5s, update: 0.5s)
        rolling_buffer = RollingAudioBuffer(window_size=2.5, update_rate=0.5, sample_rate=16000)
        
        capturer.start_capture(chunk_duration=0.4) 
        
        silence_duration = 0.0
        
        while True:
            # Puxa TODOS os pedaços acumulados na fila para evitar atrasos (latência)
            chunks = []
            while True:
                c = capturer.get_latest_chunk()
                if c:
                    chunks.append(c)
                else:
                    break
            
            if not chunks:
                # Sleep briefly to avoid busy loop se a fila estiver vazia
                time.sleep(0.01)
                continue
            
            # Processa todos os pedaços capturados de uma vez
            latest_timestamp = chunks[-1][1]
            rate = chunks[0][2]
            channels = chunks[0][3]
            
            # Combina os dados binários
            combined_data = b"".join(c[0] for c in chunks)
            
            # Calcula latência baseada no fragmento mais RECENTE retornado
            current_time = time.time()
            capture_latency_ms = (current_time - latest_timestamp) * 1000
            
            # Preprocessing
            audio_float = convert_to_float32(combined_data)
            audio_mono = to_mono(audio_float, channels)
            
            # VAD Check no bloco de áudio atual para medir o tempo de silêncio
            speech_detected, rms_val = is_speech(audio_mono, threshold=0.001)
            
            chunk_duration_sec = len(audio_mono) / rate
            
            if not speech_detected:
                silence_duration += chunk_duration_sec
                
                # Só limpa o buffer se o silêncio durar mais de 2.5 segundos.
                # Se for apenas uma pausa entre palavras (ex: 0.3s), mantemos no buffer!
                if silence_duration > 2.5:
                    rolling_buffer.clear()
                    translator.clear_state()
                    print(".", end="", flush=True)
                    continue 
            else:
                silence_duration = 0.0
                
            audio_resampled = resample_audio(audio_mono, rate, 16000)

            # Adiciona ao buffer contínuo (short silences são incluídos para continuidade)
            window_to_transcribe = rolling_buffer.append(audio_resampled)
            
            if window_to_transcribe is not None:
                # Transcribe
                text, processing_time_ms = transcriber.transcribe(window_to_transcribe, language="en")
                
                if text:
                    translated_text, trans_time_ms = translator.incremental_translate(text)
                    if translated_text:
                        print(f"\n[EN] {text}")
                        print(f"[PT] {translated_text} (W:{processing_time_ms:.0f}ms | T:{trans_time_ms:.0f}ms | Latency:{capture_latency_ms:.0f}ms)")
                else:
                    print(".", end="", flush=True) # visual feedback for silence/no text
            
            # Sleep briefly to avoid busy loop if buffer is empty, 
            # but short enough to consume quickly
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping capture...")
    finally:
        capturer.close()

if __name__ == "__main__":
    main()