import unittest
import sys
import os
import tkinter as tk

# Adiciona o diretório raiz do projeto ao sys.path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from overlay.subtitle_window import SubtitleOverlay

class TestSubtitleOverlay(unittest.TestCase):
    def setUp(self):
        # Inicializa a classe de overlay para os testes
        self.overlay = SubtitleOverlay(font_size=12)
        
    def tearDown(self):
        # Garante que a janela e o loop do tkinter sejam destruídos após cada teste
        # para que um teste não influencie o outro.
        if hasattr(self, "overlay") and hasattr(self.overlay, "root"):
            try:
                self.overlay.root.destroy()
            except tk.TclError:
                pass # A janela já foi destruída pelo teste
            
    def test_initialization(self):
        """Testa se a janela inicializa com as configurações corretas (bg black para Chroma Key)."""
        self.assertIsInstance(self.overlay.root, tk.Tk)
        self.assertEqual(self.overlay.root.cget('bg'), 'black')
        self.assertEqual(self.overlay.label.cget('bg'), 'black')
        self.assertEqual(self.overlay.label.cget("text"), "Legenda ativada. Aguardando aúdio...")
        
    def test_update_text_queue(self):
        """Testa se o método update_text adiciona a mensagem de forma assíncrona na fila interna."""
        self.overlay.update_text("Hello World!")
        
        # A fila não deve estar vazia
        self.assertFalse(self.overlay.text_queue.empty())
        
        # Pega o primeiro item e checa se é igual ao inserido
        item = self.overlay.text_queue.get()
        self.assertEqual(item, "Hello World!")
        
    def test_close_signals_queue(self):
        """Testa se o método close insere o sinalizador secreto de término (None) na fila."""
        self.overlay.close()
        
        # Deve ter adicionado um None
        item = self.overlay.text_queue.get()
        self.assertIsNone(item)
        
    def test_visual_display(self):
        """
        Teste visual focado em renderizar a janela brevemente durante a suíte.
        O Tkinter será forçado a iniciar por 2 segundos reais para o usuário visualizar.
        """
        import time
        import threading
        
        def simulate_text():
            time.sleep(0.5)
            self.overlay.update_text("Teste visual: renderizando a janela...")
            time.sleep(1.5)
            self.overlay.close()
            
        # Roda um script leve no fundo para disparar o texto e depois sinalizar o fechamento
        threading.Thread(target=simulate_text, daemon=True).start()
        
        # Inicia a UI (isso vai travar a thread de testes até o simulate_text enviar o sinal de close)
        self.overlay.start()
        
if __name__ == '__main__':
    unittest.main()
