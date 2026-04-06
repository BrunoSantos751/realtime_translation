from RealtimeSTT import AudioToTextRecorder
import threading

from translation.translator import TranslationEngine


class RealtimeSTTTranscriber:
    """
    Motor STT usando RealtimeSTT que substitui o WhisperTranscriber.
    - VAD interno (SileroVAD) elimina o VAD manual.
    - Usa feed_audio() com chunks do loopback (sem microfone direto).
    - Transcricao streaming: atualiza o overlay DURANTE a fala com texto traduzido.
    - Texto final traduzido com contexto (quando SileroVAD detecta fim de fala).
    - feed_audio exige 16-bit mono PCM a 16kHz (compativel com nosso preprocess).
    """

    def __init__(self, model_name="base", language="en", on_realtime_text=None, on_final_text=None):
        self.language = language
        self._recorder = None
        self._ready = threading.Event()
        self._translator = TranslationEngine()
        self._text_thread = None

        # Callback parcial: traduz incrementalmente e envia para o overlay
        def _wrap_realtime_callback(raw_text: str):
            if not raw_text.strip():
                self._translator.clear_state()
                if on_realtime_text:
                    on_realtime_text("")
                return
            translated, _ = self._translator.incremental_translate(raw_text)
            print(f"\r[RT] EN: {raw_text}  |  PT: {translated}", end="", flush=True)
            if on_realtime_text:
                on_realtime_text(translated)

        # Wrapper para texto final: traduz com contexto (reset incremental + traduz tudo)
        def _wrap_final_callback(raw_text: str):
            if not raw_text.strip():
                self._translator.clear_state()
                return
            # Limpa estado incremental e traduz o texto completo para contexto
            self._translator.clear_state()
            translated, _ = self._translator.incremental_translate(raw_text)
            print(f"\n[FN] EN: {raw_text}  |  PT: {translated}")
            if on_final_text:
                on_final_text(translated)

        print(f"Loading RealtimeSTT model '{model_name}' (language={language})...")
        self._recorder = AudioToTextRecorder(
            model=model_name,
            language=self.language,
            use_microphone=False,
            beam_size=1,
            enable_realtime_transcription=True,
            realtime_processing_pause=0.1,
            on_realtime_transcription_update=_wrap_realtime_callback,
        )

        # .text() e seu loop de texto finalizado rodam em thread separada
        import threading as _th
        def _text_loop():
            try:
                while True:
                    self._recorder.text(_wrap_final_callback)
            except Exception:
                pass

        self._text_thread = _th.Thread(target=_text_loop, daemon=True)
        self._text_thread.start()

        print("RealtimeSTT model loaded.")
        self._ready.set()

    def feed_audio(self, audio_int16_mono_bytes):
        """Alimenta o STT com chunk de audio 16-bit mono PCM a 16kHz."""
        if self._ready.is_set():
            self._recorder.feed_audio(audio_int16_mono_bytes)

    def abort(self):
        if self._ready.is_set():
            self._recorder.abort()
            self._translator.clear_state()

    def reset(self):
        if self._ready.is_set():
            self._recorder.reset()
            self._translator.clear_state()

    def shutdown(self):
        if self._recorder:
            self._recorder.shutdown()
        if self._text_thread and self._text_thread.is_alive():
            self._text_thread.join(timeout=5)
