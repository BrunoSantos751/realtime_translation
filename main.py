from audio.capture import AudioCapture
import time
import threading
import queue
from speech.whisper_engine import WhisperTranscriber

from audio.preprocess import convert_to_float32, to_mono, resample_audio, is_speech
from pipeline.rolling_buffer import RollingAudioBuffer
from overlay.subtitle_window import SubtitleOverlay
from translation.translator import TranslationEngine

def stt_worker_loop(stt_queue: queue.Queue, overlay: SubtitleOverlay):
    """
    Background worker that runs the heavy STT and Translation models.
    It reads audio windows from the queue and updates the UI overlay.
    """
    print("\n[Worker] Initializing models in background thread...")
    # Initialize Transcriber
    transcriber = WhisperTranscriber(model_name="base") # tiny, base, small, medium, large
    translator = TranslationEngine()
    print("[Worker] Ready for transcription.")
    
    while True:
        # Wait for a chunk to process
        item = stt_queue.get()
        if item is None:
            # Break signal
            break
            
        window_to_transcribe, capture_latency_ms, is_clear_signal = item
        
        if is_clear_signal:
            translator.clear_state()
            overlay.update_text("") # Limpa a legenda na tela
            stt_queue.task_done()
            continue
            
        # Transcribe
        text, processing_time_ms = transcriber.transcribe(window_to_transcribe, language="en")
        
        if text:
            translated_text, trans_time_ms = translator.incremental_translate(text)
            if translated_text:
                print(f"\n[EN] {text}")
                print(f"[PT] {translated_text} (W:{processing_time_ms:.0f}ms | T:{trans_time_ms:.0f}ms | Latency:{capture_latency_ms:.0f}ms)")
                overlay.update_text(translated_text) # Atualiza a legenda na tela
        else:
            print(".", end="", flush=True) # visual feedback for silence/no text
            
        stt_queue.task_done()

def audio_processing_loop(overlay: SubtitleOverlay):
    capturer = AudioCapture()
    # Queue size 1 means we only keep the absolute freshest window to transcribe
    # If a new window arrives while whisper is busy, we will overwrite the old pending one.
    stt_queue = queue.Queue(maxsize=1)
    
    # Start the background worker thread
    worker_thread = threading.Thread(target=stt_worker_loop, args=(stt_queue, overlay), daemon=True)
    worker_thread.start()
    
    try:
        print("Listing valid loopback devices:")
        # Just listing for demonstration
        devices = capturer.list_devices()
        
        print("\nStarting capture (Press Ctrl+C to stop)...")
        
        # Inicia o rolling buffer (janela: 1.5s, update: 0.2s) - reduced update for lower latency
        rolling_buffer = RollingAudioBuffer(window_size=1.5, update_rate=0.2, sample_rate=16000)
        
        # Reduced chunk duration to 0.2s for lower baseline latency
        capturer.start_capture(chunk_duration=0.2) 
        
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
                
                # Só limpa o buffer se o silêncio durar mais de 1.5 segundos.
                if silence_duration > 1.5:
                    rolling_buffer.clear()
                    
                    # Push a clear signal to the queue, replacing any pending transcription
                    try:
                        if stt_queue.full():
                            stt_queue.get_nowait()
                        stt_queue.put_nowait((None, 0, True))
                    except (queue.Empty, queue.Full):
                        pass

                    print(".", end="", flush=True)
                    continue 
            else:
                silence_duration = 0.0
                
            audio_resampled = resample_audio(audio_mono, rate, 16000)

            # Adiciona ao buffer contínuo
            window_to_transcribe = rolling_buffer.append(audio_resampled)
            
            if window_to_transcribe is not None:
                # Put the latest window to be transcribed in the queue.
                # If the worker is still busy from a previous window, drop the old one and keep the latest.
                item = (window_to_transcribe, capture_latency_ms, False)
                try:
                    if stt_queue.full():
                        stt_queue.get_nowait() # Remove old
                    stt_queue.put_nowait(item) # Set new
                except (queue.Empty, queue.Full):
                    pass
            
            # Sleep briefly to avoid busy loop
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping capture...")
        stt_queue.put(None) # Signal worker to stop
        overlay.close()
    except Exception as e:
        print(f"\nError in audio processing loop: {e}")
        stt_queue.put(None)
        overlay.close()
    finally:
        capturer.close()

def main():
    print("Inicializando Overlay de Legendas...")
    overlay = SubtitleOverlay(font_size=32)
    
    # Inicia o processamento de áudio em uma thread separada (background)
    audio_thread = threading.Thread(target=audio_processing_loop, args=(overlay,), daemon=True)
    audio_thread.start()
    
    # Inicia o loop principal do Tkinter (UI) na thread principal
    # Isso vai travar a thread atual até a janela ser fechada
    try:
        overlay.start()
    except KeyboardInterrupt:
        print("\nEncerrando aplicação...")
        overlay.close()

if __name__ == "__main__":
    main()