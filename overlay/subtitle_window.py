import tkinter as tk
import threading
import queue
import time

class SubtitleOverlay:
    def __init__(self, font_family="Arial", font_size=28, text_color="#FFFF00"):
        """
        Inicializa o overlay transparente de legendas.
        Usa preto ('black') como cor de Chroma Key para o Windows ignorar e deixar invisível.
        """
        self.root = tk.Tk()
        
        # Oculta a janela brevemente durante a construção para evitar "pulos" visuais
        self.root.withdraw()
        
        # Remove bordas e barra de título do Windows
        self.root.overrideredirect(True)
        
        # Janela sempre no topo
        self.root.wm_attributes("-topmost", True)
        
        # Define a cor do Chroma Key: o Windows vai sumir com tudo que for exatamente 'black'
        bg_color = 'black'
        self.root.config(bg=bg_color)
        self.root.wm_attributes("-transparentcolor", bg_color)
        
        # Elemento de Texto da Legenda
        self.label = tk.Label(
            self.root, 
            text="Legenda ativada. Aguardando aúdio...", 
            font=(font_family, font_size, 'bold'),
            fg=text_color,  # Cor da fonte (Amarelo por padrão para alto contraste)
            bg=bg_color,    # O fundo do Label deve ser o mesmo do chroma key
            wraplength=1000, # Largura máxima antes de quebrar a linha (em pixels)
            justify="center"
        )
        self.label.pack(padx=20, pady=20)
        
        # Fila thread-safe para receber atualizações do main.py
        self.text_queue = queue.Queue()
        
        self._recenter_window()
        self.root.deiconify() # Revela a janela
        
        # Inicia loop de leitura da fila
        self._check_queue()

    def _recenter_window(self):
        """Centraliza a janela na parte inferior da tela, como legendas comuns."""
        self.root.update_idletasks() # Garante que as dimensões foram computadas
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        
        window_width = self.root.winfo_width()
        
        # x centralizado, y na parte inferior (com margem de 150 pixels)
        x = (screen_width // 2) - (window_width // 2)
        y = screen_height - 150 
        
        self.root.geometry(f"+{x}+{y}")

    def _check_queue(self):
        """Pool de atualizações: verifica periodicamente se há novo texto para exibir."""
        try:
            while True:
                new_text = self.text_queue.get_nowait()
                if new_text is None:  # Sinal secreto de parada
                    self.root.destroy()
                    return
                
                # Atualiza o texto na interface
                self.label.config(text=new_text)
                
                # Reposiciona caso o texto tenha feito a janela mudar de largura/altura
                self._recenter_window()
                
        except queue.Empty:
            pass
        
        # Continua checando a cada 50ms (rápido o suficiente para tempo real, leve para CPU)
        self.root.after(50, self._check_queue)
        
    def update_text(self, text):
        """Método público e thread-safe para atualizar o texto da legenda."""
        self.text_queue.put(text)
        
    def close(self):
        """Sinaliza para a janela fechar de forma segura."""
        self.text_queue.put(None)
        
    def start(self):
        """
        Trava a thread atual e inicializa a interface (Loop do Tkinter).
        Deve ser chamado na Main Thread do Python idealmente.
        """
        self.root.mainloop()

# Bloco de testes isolado
if __name__ == "__main__":
    overlay = SubtitleOverlay(font_size=32)
    
    def simulate_translation_pipeline():
        """Simula um sistema externo (ex: o whisper) enviando texto em tempo real"""
        time.sleep(2)
        overlay.update_text("Hello!")
        time.sleep(1)
        overlay.update_text("Esta é uma legenda...")
        time.sleep(2)
        overlay.update_text("Ela possui fundo 100% invisível!")
        time.sleep(2)
        overlay.update_text("A janela e as bordas também sumiram de verdade.")
        time.sleep(3)
        overlay.update_text("Legal, né? Fechando em 2 segundos...")
        time.sleep(2)
        overlay.close()
        
    # Inicia as simulações em background
    threading.Thread(target=simulate_translation_pipeline, daemon=True).start()
    
    # Inicia a UI no main thread
    overlay.start()
