import time
import argostranslate.package
import argostranslate.translate

class TranslationEngine:
    def __init__(self, from_code="en", to_code="pt"):
        print(f"Loading Argos Translate for {from_code}->{to_code}...")
        self.from_code = from_code
        self.to_code = to_code
        self.previous_english_text = ""
        self._ensure_package_installed()
        print("Translation model loaded.")

    def _ensure_package_installed(self):
        # Check if installed
        installed_packages = argostranslate.package.get_installed_packages()
        for pkg in installed_packages:
            if pkg.from_code == self.from_code and pkg.to_code == self.to_code:
                return
        
        print("Language package not found locally. Downloading from Argos Translate index...")
        argostranslate.package.update_package_index()
        available_packages = argostranslate.package.get_available_packages()
        package_to_install = next(
            filter(
                lambda x: x.from_code == self.from_code and x.to_code == self.to_code, 
                available_packages
            ), None
        )
        if package_to_install:
            print(f"Installing {self.from_code}->{self.to_code} package...")
            argostranslate.package.install_from_path(package_to_install.download())
            print("Finished installing package.")
        else:
            print(f"Error: Could not find language package for {self.from_code}->{self.to_code}.")
        
    def incremental_translate(self, current_english_text):
        """
        Translates only the new portion of the text that hasn't been translated yet.
        Returns the translated string and the processing time in ms.
        """
        current_english_text = current_english_text.strip()
        if not current_english_text:
            return "", 0.0
            
        new_text = current_english_text
        
        if self.previous_english_text:
            words_prev = self.previous_english_text.split()
            words_curr = current_english_text.split()
            
            overlap_idx = 0
            limit = min(len(words_prev), len(words_curr))
            
            def clean_word(w):
                # Remove common ending punctuation for comparison
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
                
        self.previous_english_text = current_english_text
        
        if not new_text.strip():
            return "", 0.0
            
        start_time = time.time()
        # Translate the text using argostranslate
        translation = argostranslate.translate.translate(new_text, self.from_code, self.to_code)
        processing_time_ms = (time.time() - start_time) * 1000
        
        return translation, processing_time_ms

    def clear_state(self):
        """Clears the translation history."""
        self.previous_english_text = ""
