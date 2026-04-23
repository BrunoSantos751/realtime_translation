from RealtimeSTT import AudioToTextRecorder
import threading

from translation.translator import TranslationEngine


class RealtimeSTTTranscriber:
    """
    Motor STT usando RealtimeSTT que substitui o WhisperTranscriber.
    - VAD interno (SileroVAD) elimina o VAD manual.
    - Usa feed_audio() com chunks do loopback (sem microfone direto).
    - Transcrição streaming: atualiza o overlay DURANTE a fala com texto traduzido.
    - Texto final traduzido com contexto (quando SileroVAD detecta fim de fala).
    - feed_audio exige 16-bit mono PCM a 16kHz (compatível com nosso preprocess).
    """

    def __init__(
        self,
        model_name: str = "base",
        src_lang: str = "en",
        tgt_lang: str = "pt",
        translate: bool = True,
        on_realtime_text=None,
        on_final_text=None,
    ):
        self.src_lang = src_lang
        self._recorder = None
        self._ready = threading.Event()

        # Cria o motor de tradução (modo passthrough se translate=False ou src==tgt)
        effective_tgt = tgt_lang if (translate and tgt_lang != src_lang) else src_lang
        self._translator = TranslationEngine(from_code=src_lang, to_code=effective_tgt)

        self._text_thread = None

        # Callback parcial: traduz/passthrough incrementalmente e envia para o overlay
        def _wrap_realtime_callback(raw_text: str):
            if not raw_text.strip():
                self._translator.clear_state()
                if on_realtime_text:
                    on_realtime_text("")
                return
            result, _ = self._translator.incremental_translate(raw_text)
            if self._translator.needs_translation:
                print(f"\r[RT] {src_lang.upper()}: {raw_text}  |  {tgt_lang.upper()}: {result}", end="", flush=True)
            else:
                print(f"\r[RT] {src_lang.upper()}: {raw_text}", end="", flush=True)
            if on_realtime_text:
                on_realtime_text(result)

        # Wrapper para texto final: traduz com contexto (reset incremental + traduz tudo)
        def _wrap_final_callback(raw_text: str):
            if not raw_text.strip():
                self._translator.clear_state()
                return
            self._translator.clear_state()
            result, _ = self._translator.incremental_translate(raw_text)
            if self._translator.needs_translation:
                print(f"\n[FN] {src_lang.upper()}: {raw_text}  |  {tgt_lang.upper()}: {result}")
            else:
                print(f"\n[FN] {src_lang.upper()}: {raw_text}")
            if on_final_text:
                on_final_text(result)

        print(f"Carregando modelo RealtimeSTT '{model_name}' (idioma de entrada={src_lang})...")
        self._recorder = AudioToTextRecorder(
            model=model_name,
            language=src_lang,
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

        print("Modelo RealtimeSTT carregado.")
        self._ready.set()

    def feed_audio(self, audio_int16_mono_bytes: bytes):
        """Alimenta o STT com chunk de áudio 16-bit mono PCM a 16kHz."""
        if self._ready.is_set():
            self._recorder.feed_audio(audio_int16_mono_bytes)

    def abort(self):
        if self._ready.is_set():
            self._recorder.abort()
            self._translator.clear_state()

    def reset(self):
        if self._ready.is_set():
            # self._recorder.reset() # Não suportado pelo AudioToTextRecorder
            self._translator.clear_state()

    def shutdown(self):
        if self._recorder:
            self._recorder.shutdown()
        if self._text_thread and self._text_thread.is_alive():
            self._text_thread.join(timeout=5)
