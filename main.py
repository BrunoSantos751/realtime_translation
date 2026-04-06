from audio.capture import AudioCapture
import time
import threading
import numpy as np
from speech.realtimestt_engine import RealtimeSTTTranscriber
from audio.preprocess import convert_to_float32, to_mono, resample_audio
from overlay.subtitle_window import SubtitleOverlay


def audio_to_int16_mono(audio_float32: np.ndarray) -> bytes:
    """Converte float32 numpy audio para bytes PCM 16-bit mono (formato do feed_audio)."""
    audio_clipped = np.clip(audio_float32, -1.0, 1.0)
    audio_int16 = (audio_clipped * 32767.0).astype(np.int16)
    return audio_int16.tobytes()


def audio_processing_loop(overlay: SubtitleOverlay):
    capturer = AudioCapture()

    # Inicializa o STT com callbacks traduzidos que atualizam o overlay de forma thread-safe
    print("\nInicializando RealtimeSTT...")
    stt = RealtimeSTTTranscriber(
        model_name="base",
        language="en",
        on_realtime_text=lambda t: overlay.update_text(t),
        on_final_text=lambda t: overlay.update_text(t),
    )
    print("RealtimeSTT pronto.\n")

    try:
        capturer.list_devices()
        print("\nStarting capture (Press Ctrl+C to stop)...")

        # Audio por chunks curtos para minimo delay
        capturer.start_capture(chunk_duration=0.15)

        # Silencio prolongado para reset do buffer do STT
        silence_duration = 0.0
        SILENCE_THRESHOLD = 1.5  # segundos de silencio para resetar

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

            # Pre-processing
            audio_float = convert_to_float32(combined_data)
            audio_mono = to_mono(audio_float, channels)

            # VAD Check simples para medir silê ncio (mantemos para detectar pausas longas)
            rms = float(np.sqrt(np.mean(audio_mono ** 2)))
            speech_detected = rms > 0.001

            chunk_duration_sec = len(audio_mono) / rate

            if not speech_detected:
                silence_duration += chunk_duration_sec

                # Só limpa o buffer se o silêncio durar mais de 1.5 segundos.
                if silence_duration > SILENCE_THRESHOLD:
                    stt.reset()
                    overlay.update_text("")
                    silence_duration = 0.0
                    print(".", end="", flush=True)
                    continue
            else:
                silence_duration = 0.0

            # Resample para 16kHz e converte para int16 mono bytes
            audio_16k = resample_audio(audio_mono, rate, 16000)
            audio_bytes = audio_to_int16_mono(audio_16k)

            # Alimenta o RealtimeSTT - VAD interno faz o streaming
            stt.feed_audio(audio_bytes)

            # Sleep briefly to avoid busy loop
            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping capture...")
    except Exception as e:
        print(f"\nError in audio processing loop: {e}")
    finally:
        capturer.close()
        stt.shutdown()
        overlay.close()


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
