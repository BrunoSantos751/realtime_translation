from faster_whisper import WhisperModel
import numpy as np
import torch
import time

class WhisperTranscriber:
    def __init__(self, model_name="base", device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        
        # faster-whisper default configuration for compute_type
        compute_type = "float16" if self.device == "cuda" else "int8"
        
        print(f"Loading Faster Whisper model '{model_name}' on {self.device} ({compute_type})...")
        self.model = WhisperModel(model_name, device=self.device, compute_type=compute_type)
        print("Faster Whisper model loaded.")

    def transcribe(self, audio_data, language=None):
        """
        Transcribes audio data.
        :param audio_data: numpy array of audio data (float32, 16kHz, mono).
        :param language: Optional language code (e.g., "pt", "en") to guide the model.
        :return: Transcribed text.
        """
        start_time = time.time()
        
        # faster-whisper returns an iterator of segments.
        # We need to collect the text from all segments.
        # beam_size=1 for greedy and faster decoding
        segments, info = self.model.transcribe(
            audio_data, 
            language=language,
            beam_size=1,
            vad_filter=False # We already do VAD before
        )
        
        text = " ".join([segment.text for segment in segments]).strip()
        
        processing_time = (time.time() - start_time) * 1000
        return text, processing_time
