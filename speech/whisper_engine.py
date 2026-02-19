import whisper
import numpy as np
import torch
import time

class WhisperTranscriber:
    def __init__(self, model_name="base", device=None):
        self.device = device if device else ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading Whisper model '{model_name}' on {self.device}...")
        self.model = whisper.load_model(model_name, device=self.device)
        print("Whisper model loaded.")

    def transcribe(self, audio_data, language=None):
        """
        Transcribes audio data.
        :param audio_data: numpy array of audio data (float32, 16kHz, mono).
        :param language: Optional language code (e.g., "pt", "en") to guide the model.
        :return: Transcribed text.
        """
        start_time = time.time()
        
        # Optimize decoding options for speed
        # beam_size=1 (greedy), best_of=1 -> much faster
        options = dict(beam_size=1, best_of=1, fp16=False, language=language)
        
        result = self.model.transcribe(audio_data, **options)
        text = result['text'].strip()
        
        processing_time = (time.time() - start_time) * 1000
        return text, processing_time
