import tkinter as tk
import threading
import queue
import time
import ctypes
import os

class SubtitleOverlay:
    def __init__(
        self,
        font_family: str = "Arial",
        font_size: int = 28,
        text_color: str = "#FFFF00",
        position: str = "bottom-center",
        x_offset: int = 0,
        y_offset: int = 150,
        src_lang: str = "en",
        tgt_lang: str = "pt",
        translate: bool = True,
    ):
        """
        Inicializa o overlay transparente de legendas.
        Usa preto ('black') como cor de Chroma Key para o Windows ignorar e deixar invisível.
        """
        self.root = tk.Tk()

        self.position = position
        self.x_offset = x_offset
        self.y_offset = y_offset
        self._src_lang = src_lang.upper()
        self._tgt_lang = tgt_lang.upper()
        self._translate = translate

        # Oculta a janela brevemente durante a construção para evitar "pulos" visuais
        self.root.withdraw()

        # Remove bordas e barra de título do Windows
        self.root.overrideredirect(True)

        # Janela sempre no topo
        self.root.wm_attributes("-topmost", True)

        # Define a cor do Chroma Key: o Windows vai sumir com tudo que for exatamente 'black'
        bg_color = "black"
        self.root.config(bg=bg_color)
        self.root.wm_attributes("-transparentcolor", bg_color)

        # ── Indicador de idioma (canto superior esquerdo, pequeno e discreto) ──
        lang_label_text = self._build_lang_indicator()
        self.lang_label = tk.Label(
            self.root,
            text=lang_label_text,
            font=(font_family, max(10, font_size // 3), "bold"),
            fg="#00CFFF",   # Azul ciano — contrasta sem disputar atenção com a legenda
            bg=bg_color,
            anchor="w",
        )
        self.lang_label.pack(side="top", anchor="w", padx=12, pady=(6, 0))

        # ── Elemento de Texto da Legenda ──────────────────────────────────────
        self.label = tk.Label(
            self.root,
            text="Legenda ativada. Aguardando áudio...",
            font=(font_family, font_size, "bold"),
            fg=text_color,    # Amarelo por padrão para alto contraste
            bg=bg_color,      # Fundo do Label deve ser o mesmo do chroma key
            wraplength=1000,  # Largura máxima antes de quebrar a linha (em pixels)
            justify="center",
        )
        self.label.pack(padx=20, pady=(2, 20))

        # Fila thread-safe para receber atualizações do main.py
        self.text_queue = queue.Queue()

        self._update_window_position()
        self._apply_clickthrough()
        self.root.deiconify()  # Revela a janela

        # Inicia loop de leitura da fila
        self._check_queue()

    # ── Helpers ──────────────────────────────────────────────────────────────

    def _build_lang_indicator(self) -> str:
        if not self._translate or self._src_lang == self._tgt_lang:
            return f"🎙 {self._src_lang}"
        return f"🌐 {self._src_lang} → {self._tgt_lang}"

    def _apply_clickthrough(self):
        """
        No Windows, injeta estilos estendidos para a janela ignorar cliques (Click-Through)
        e ser 100% transparente a eventos do mouse.
        """
        if os.name == "nt":
            self.root.update_idletasks()
            hwnd = ctypes.windll.user32.GetParent(self.root.winfo_id())

            GWL_EXSTYLE    = -20
            WS_EX_LAYERED  = 0x00080000
            WS_EX_TRANSPARENT = 0x00000020

            current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
            new_style = current_style | WS_EX_LAYERED | WS_EX_TRANSPARENT
            ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)

    def _update_window_position(self):
        """Atualiza a posição da janela baseando-se no texto atual e configurações de âncora."""
        self.root.update_idletasks()
        screen_width  = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width  = self.root.winfo_width()
        window_height = self.root.winfo_height()

        x, y = 0, 0

        if "center" in self.position:
            x = (screen_width // 2) - (window_width // 2)
        elif "left" in self.position:
            x = self.x_offset
        elif "right" in self.position:
            x = screen_width - window_width - self.x_offset

        if "bottom" in self.position:
            y = screen_height - window_height - self.y_offset
        elif "top" in self.position:
            y = self.y_offset
        if self.position == "center":
            y = (screen_height // 2) - (window_height // 2)

        self.root.geometry(f"+{int(x)}+{int(y)}")

    def _check_queue(self):
        """Pool de atualizações: verifica periodicamente se há novo texto para exibir."""
        try:
            while True:
                new_text = self.text_queue.get_nowait()
                if new_text is None:  # Sinal secreto de parada
                    self.root.destroy()
                    return

                self.label.config(text=new_text)
                self._update_window_position()

        except queue.Empty:
            pass

        # Continua checando a cada 50ms
        self.root.after(50, self._check_queue)

    # ── API Pública ───────────────────────────────────────────────────────────

    def update_text(self, text: str):
        """Método público e thread-safe para atualizar o texto da legenda."""
        self.text_queue.put(text)

    def close(self):
        """Sinaliza para a janela fechar de forma segura."""
        self.text_queue.put(None)

    def start(self):
        """
        Trava a thread atual e inicializa a interface (Loop do Tkinter).
        Deve ser chamado na Main Thread do Python.
        """
        self.root.mainloop()


# ── Bloco de testes isolado ───────────────────────────────────────────────────
if __name__ == "__main__":
    overlay = SubtitleOverlay(font_size=32, src_lang="en", tgt_lang="pt", translate=True)

    def simulate_translation_pipeline():
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

    threading.Thread(target=simulate_translation_pipeline, daemon=True).start()
    overlay.start()
