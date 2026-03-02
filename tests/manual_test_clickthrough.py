import sys
import os
import time
import threading

# Adiciona o diretório raiz do projeto ao sys.path para importar os módulos
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from overlay.subtitle_window import SubtitleOverlay

def run_manual_test():
    print("Iniciando teste manual de Click-Through e Posicionamento...")
    print("A janela de legenda aparecerá na área inferior central da tela.")
    print("Instruções:")
    print("1. Coloque um vídeo, navegado ou jogo atrás do texto.")
    print("2. Tente clicar exatamente sobre o texto amarelo.")
    print("3. O clique DEVE passar pela legenda e atingir o aplicativo de trás (Click-Through).")
    print("O teste durará 15 segundos.\n")
    
    # Inicia o overlay na posição padrão bottom-center
    overlay = SubtitleOverlay(font_size=32, position="bottom-center")
    
    def simulate_subtitles():
        messages = [
            "Teste de Click-Through Habilitado.",
            "Tente clicar aqui! (O clique deve ir para trás)",
            "A janela deve ser 100% transparente ao mouse.",
            "Posição atual: bottom-center.",
            "Testando reposicionamento dinâmico em 3...",
            "Testando reposicionamento dinâmico em 2...",
            "Testando reposicionamento dinâmico em 1...",
            "Fim do teste, fechando..."
        ]
        
        for msg in messages:
            time.sleep(2)
            overlay.update_text(msg)
            
        time.sleep(2)
        overlay.close()
        print("Teste finalizado.")

    # Roda as legendas simuladas em background
    threading.Thread(target=simulate_subtitles, daemon=True).start()
    
    # Trava a thread principal na UI
    overlay.start()

if __name__ == "__main__":
    run_manual_test()
