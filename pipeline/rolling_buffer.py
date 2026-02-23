import numpy as np

class RollingAudioBuffer:
    """
    Mantém um buffer contínuo de áudio para processamento em tempo real (rolling buffer).
    Permite adicionar pequenos trechos de áudio (ex: 0.3s ou 0.4s) e extrair janelas maiores
    (ex: 2.0s ou 2.5s) a uma taxa de atualização específica (ex: 0.5s).
    """
    def __init__(self, window_size=2.5, update_rate=0.5, sample_rate=16000):
        self.window_size = window_size
        self.update_rate = update_rate
        self.sample_rate = sample_rate
        
        self.buffer = np.array([], dtype=np.float32)
        self.samples_since_last_update = 0
        self.has_first_window = False
        
        # Limite do buffer global para evitar estouro de memória (ex: limite de 10 segundos)
        self.max_buffer_size = int(10 * sample_rate)

    def append(self, new_audio: np.ndarray):
        """
        Adiciona novo áudio ao buffer global.
        Retorna o frame para transcrição se a taxa de atualização for atingida e
        houver áudio suficiente para uma janela, caso contrário retorna None.
        """
        self.buffer = np.concatenate((self.buffer, new_audio))
        self.samples_since_last_update += len(new_audio)
        
        # Mantém o buffer global em um tamanho máximo
        if len(self.buffer) > self.max_buffer_size:
            self.buffer = self.buffer[-self.max_buffer_size:]
            
        window_samples = int(self.window_size * self.sample_rate)
        update_samples = int(self.update_rate * self.sample_rate)
        
        # Lógica para retornar o frame:
        # Se ainda não atingiu a primeira janela completa de (ex: 2s ou 2.5s)
        if len(self.buffer) >= window_samples:
            if not self.has_first_window:
                self.has_first_window = True
                self.samples_since_last_update = 0
                return self.buffer[-window_samples:]
            
            # Depois da primeira janela, atualiza conforme a taxa de update (ex: 0.5s)
            if self.samples_since_last_update >= update_samples:
                # Usamos modulo caso um chunk maior que update_samples seja inserido
                # para que não emita múltiplas vezes acidentalmente em um único update.
                self.samples_since_last_update %= update_samples
                return self.buffer[-window_samples:]
        
        return None

    def clear(self):
        """Limpa o buffer global."""
        self.buffer = np.array([], dtype=np.float32)
        self.samples_since_last_update = 0
        self.has_first_window = False
