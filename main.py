import argparse
import threading
import time

import numpy as np

from audio.capture import AudioCapture
from audio.preprocess import convert_to_float32, to_mono, resample_audio
from config.languages import (
    WHISPER_LANGUAGES,
    is_pair_supported,
    is_whisper_supported,
    print_supported_languages,
)
from overlay.subtitle_window import SubtitleOverlay
from speech.realtimestt_engine import RealtimeSTTTranscriber


# ── Helpers ───────────────────────────────────────────────────────────────────

def audio_to_int16_mono(audio_float32: np.ndarray) -> bytes:
    """Converte float32 numpy audio para bytes PCM 16-bit mono (formato do feed_audio)."""
    audio_clipped = np.clip(audio_float32, -1.0, 1.0)
    audio_int16 = (audio_clipped * 32767.0).astype(np.int16)
    return audio_int16.tobytes()


# ── Loop de processamento de áudio (thread de background) ────────────────────

def audio_processing_loop(
    overlay: SubtitleOverlay,
    stop_event: threading.Event,
    model_name: str,
    src_lang: str,
    tgt_lang: str,
    translate: bool,
):
    capturer = AudioCapture()

    print("\nInicializando RealtimeSTT...")
    stt = RealtimeSTTTranscriber(
        model_name=model_name,
        src_lang=src_lang,
        tgt_lang=tgt_lang,
        translate=translate,
        on_realtime_text=lambda t: overlay.update_text(t),
        on_final_text=lambda t: overlay.update_text(t),
    )
    print("RealtimeSTT pronto.\n")

    try:
        capturer.list_devices()
        print("\nStarting capture (Press Ctrl+C to stop)...")

        # Chunks curtos para mínimo delay
        capturer.start_capture(chunk_duration=0.15)

        # Silêncio prolongado → reset do buffer do STT
        silence_duration = 0.0
        SILENCE_THRESHOLD = 1.5  # segundos de silêncio para resetar

        while not stop_event.is_set():
            # Puxa TODOS os pedaços acumulados na fila para evitar atrasos
            chunks = []
            while True:
                c = capturer.get_latest_chunk()
                if c:
                    chunks.append(c)
                else:
                    break

            if not chunks:
                time.sleep(0.01)
                continue

            # Junta os chunks capturados
            rate     = chunks[0][2]
            channels = chunks[0][3]
            combined_data = b"".join(c[0] for c in chunks)

            # Pré-processamento
            audio_float = convert_to_float32(combined_data)
            audio_mono  = to_mono(audio_float, channels)

            # VAD simples por RMS para detectar pausas longas
            rms = float(np.sqrt(np.mean(audio_mono ** 2)))
            speech_detected = rms > 0.001
            chunk_duration_sec = len(audio_mono) / rate

            if not speech_detected:
                silence_duration += chunk_duration_sec
                if silence_duration > SILENCE_THRESHOLD:
                    stt.reset()
                    overlay.update_text("")
                    silence_duration = 0.0
                    print(".", end="", flush=True)
                    continue
            else:
                silence_duration = 0.0

            # Resample para 16kHz e converte para int16 mono bytes
            audio_16k  = resample_audio(audio_mono, rate, 16000)
            audio_bytes = audio_to_int16_mono(audio_16k)

            # Alimenta o RealtimeSTT — VAD interno faz o streaming
            stt.feed_audio(audio_bytes)

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("\nStopping capture...")
    except Exception as e:
        print(f"\nError in audio processing loop: {e}")
    finally:
        capturer.close()
        stt.shutdown()
        overlay.close()


# ── Parsing de argumentos ─────────────────────────────────────────────────────

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="realtime_translation",
        description="Transcrição e tradução em tempo real do áudio do sistema.",
        formatter_class=argparse.RawTextHelpFormatter,
    )

    parser.add_argument(
        "--src", "-s",
        metavar="LANG",
        default="en",
        help=(
            "Idioma de origem para transcrição (Whisper).\n"
            "Padrão: en (English)\n"
            "Exemplo: --src es  (Espanhol)"
        ),
    )
    parser.add_argument(
        "--tgt", "-t",
        metavar="LANG",
        default="pt",
        help=(
            "Idioma de destino para tradução (Argos Translate).\n"
            "Padrão: pt (Portuguese)\n"
            "Exemplo: --tgt fr  (Francês)"
        ),
    )
    parser.add_argument(
        "--model", "-m",
        metavar="MODEL",
        default="base",
        choices=["tiny", "base", "small", "medium", "large", "large-v2", "large-v3"],
        help=(
            "Modelo Whisper para transcrição.\n"
            "Opções: tiny, base, small, medium, large, large-v2, large-v3\n"
            "Padrão: base"
        ),
    )
    parser.add_argument(
        "--no-translate",
        action="store_true",
        default=False,
        help="Desativa a tradução. O overlay exibe apenas a transcrição bruta.",
    )
    parser.add_argument(
        "--list-langs",
        action="store_true",
        default=False,
        help="Lista todos os idiomas e pares de tradução disponíveis e encerra.",
    )

    return parser.parse_args()


def validate_args(args: argparse.Namespace) -> bool:
    """Valida os argumentos e imprime avisos. Retorna False se inválido."""
    if not is_whisper_supported(args.src):
        print(f"[ERRO] Idioma de origem '{args.src}' não é suportado pelo Whisper.")
        print(f"       Use 'python main.py --list-langs' para ver os idiomas disponíveis.")
        return False

    if not args.no_translate and args.src != args.tgt:
        if not is_whisper_supported(args.tgt):
            # tgt não precisa ser Whisper, apenas Argos — avisamos mas não bloqueamos
            pass
        if not is_pair_supported(args.src, args.tgt):
            print(f"[AVISO] Par '{args.src}'->'{ args.tgt}' não está no catálogo verificado do Argos.")
            print(f"        O sistema tentará baixar o pacote automaticamente.")
            print(f"        Use '--list-langs' para ver os pares garantidos.\n")

    return True


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    args = parse_args()

    # --list-langs: imprime catálogo e sai
    if args.list_langs:
        print_supported_languages()
        return

    # Valida os idiomas informados
    if not validate_args(args):
        return

    translate = not args.no_translate

    # Log de configuração inicial
    print("=" * 50)
    print(f"  Realtime Translation")
    print(f"  Modelo  : {args.model}")
    print(f"  Idioma  : {args.src.upper()} ({WHISPER_LANGUAGES.get(args.src, args.src)})")
    if translate and args.src != args.tgt:
        print(f"  Tradução: {args.src.upper()} → {args.tgt.upper()}")
    else:
        print(f"  Tradução: DESATIVADA (modo transcrição)")
    print("=" * 50)
    print()

    print("Inicializando Overlay de Legendas...")
    overlay = SubtitleOverlay(
        font_size=32,
        src_lang=args.src,
        tgt_lang=args.tgt,
        translate=translate,
    )

    # Evento para sinalizar encerramento da thread de áudio
    stop_event = threading.Event()

    # Inicia o processamento de áudio em thread de background
    audio_thread = threading.Thread(
        target=audio_processing_loop,
        args=(overlay, stop_event, args.model, args.src, args.tgt, translate),
        daemon=True,
    )
    audio_thread.start()

    # Loop principal do Tkinter (UI) na thread principal
    try:
        overlay.start()
    except KeyboardInterrupt:
        print("\nEncerrando aplicação via teclado...")
    finally:
        print("\nSinalizando encerramento para as threads em background...")
        stop_event.set()
        audio_thread.join(timeout=3.0)
        overlay.close()


if __name__ == "__main__":
    main()
