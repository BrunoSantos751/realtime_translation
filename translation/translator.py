import time
import argostranslate.package
import argostranslate.translate

class TranslationEngine:
    def __init__(self, from_code="en", to_code="pt"):
        self.from_code = from_code
        self.to_code = to_code
        self.previous_english_text = ""
        self._translation_available = False

        # Modo passthrough: sem tradução quando os idiomas são iguais
        if from_code == to_code:
            print(f"[TranslationEngine] Idioma de origem == destino ({from_code}). Modo passthrough ativo (sem tradução).")
            self._translation_available = False
            return

        print(f"Carregando Argos Translate para {from_code}->{to_code}...")
        self._translation_available = self._ensure_package_installed()
        if self._translation_available:
            print("Modelo de tradução carregado.")
        else:
            print(f"[AVISO] Par {from_code}->{to_code} não disponível. O texto transcrito será exibido sem tradução.")

    def _ensure_package_installed(self) -> bool:
        """
        Garante que o pacote Argos para o par (from_code, to_code) está instalado.
        Retorna True se a tradução está disponível, False caso contrário.
        """
        # Verifica se já está instalado
        installed_packages = argostranslate.package.get_installed_packages()
        for pkg in installed_packages:
            if pkg.from_code == self.from_code and pkg.to_code == self.to_code:
                return True

        # Tenta baixar e instalar
        print(f"Pacote {self.from_code}->{self.to_code} não encontrado localmente. Baixando do índice do Argos...")
        try:
            argostranslate.package.update_package_index()
            available_packages = argostranslate.package.get_available_packages()
            package_to_install = next(
                filter(
                    lambda x: x.from_code == self.from_code and x.to_code == self.to_code,
                    available_packages
                ), None
            )
            if package_to_install:
                print(f"Instalando pacote {self.from_code}->{self.to_code}...")
                argostranslate.package.install_from_path(package_to_install.download())
                print("Pacote instalado com sucesso.")
                return True
            else:
                print(f"[ERRO] Par {self.from_code}->{self.to_code} não encontrado no índice do Argos.")
                print(f"       Use 'python main.py --list-langs' para ver os pares disponíveis.")
                return False
        except Exception as e:
            print(f"[ERRO] Falha ao instalar pacote de tradução: {e}")
            return False

    @property
    def needs_translation(self) -> bool:
        """True se a tradução está configurada e disponível."""
        return self._translation_available and self.from_code != self.to_code

    def incremental_translate(self, current_text: str):
        """
        Se a tradução estiver disponível, traduz apenas as palavras novas do texto.
        Caso contrário (passthrough), retorna o texto original sem modificações.
        Retorna (texto_resultado, tempo_ms).
        """
        current_text = current_text.strip()
        if not current_text:
            return "", 0.0

        # Modo passthrough: sem tradução
        if not self.needs_translation:
            self.previous_english_text = current_text
            return current_text, 0.0

        # Calcula apenas o trecho novo desde o último update
        new_text = current_text
        if self.previous_english_text:
            words_prev = self.previous_english_text.split()
            words_curr = current_text.split()

            overlap_idx = 0
            limit = min(len(words_prev), len(words_curr))

            def clean_word(w):
                return w.lower().strip(".,!?\"'")

            for i in range(limit):
                if clean_word(words_prev[i]) == clean_word(words_curr[i]):
                    overlap_idx = i + 1
                else:
                    break

            if overlap_idx < len(words_curr):
                new_text = " ".join(words_curr[overlap_idx:])
            else:
                new_text = ""

        self.previous_english_text = current_text

        if not new_text.strip():
            return "", 0.0

        start_time = time.time()
        translation = argostranslate.translate.translate(new_text, self.from_code, self.to_code)
        processing_time_ms = (time.time() - start_time) * 1000

        return translation, processing_time_ms

    def clear_state(self):
        """Limpa o histórico de tradução incremental."""
        self.previous_english_text = ""
