"""
Catálogo de idiomas verificados contra as bibliotecas reais do projeto.

- WHISPER_LANGUAGES: 100 idiomas suportados pelo faster-whisper para STT (transcrição).
- ARGOS_PAIRS: 91 pares src->tgt disponíveis para download no Argos Translate.
  Apenas pares cujo `from_code` também existe no Whisper são incluídos.

Verificado em 2026-04-22 com:
  - faster-whisper 1.1.1
  - argostranslate (índice online, 98 pacotes disponíveis, 1 instalado)
"""

# ─── Idiomas suportados pelo Whisper (STT) ─────────────────────────────────
# Código ISO 639-1 (ou BCP-47 curto) → nome em inglês
WHISPER_LANGUAGES: dict[str, str] = {
    "af": "Afrikaans",
    "am": "Amharic",
    "ar": "Arabic",
    "as": "Assamese",
    "az": "Azerbaijani",
    "ba": "Bashkir",
    "be": "Belarusian",
    "bg": "Bulgarian",
    "bn": "Bengali",
    "bo": "Tibetan",
    "br": "Breton",
    "bs": "Bosnian",
    "ca": "Catalan",
    "cs": "Czech",
    "cy": "Welsh",
    "da": "Danish",
    "de": "German",
    "el": "Greek",
    "en": "English",
    "es": "Spanish",
    "et": "Estonian",
    "eu": "Basque",
    "fa": "Persian",
    "fi": "Finnish",
    "fo": "Faroese",
    "fr": "French",
    "gl": "Galician",
    "gu": "Gujarati",
    "ha": "Hausa",
    "haw": "Hawaiian",
    "he": "Hebrew",
    "hi": "Hindi",
    "hr": "Croatian",
    "ht": "Haitian Creole",
    "hu": "Hungarian",
    "hy": "Armenian",
    "id": "Indonesian",
    "is": "Icelandic",
    "it": "Italian",
    "ja": "Japanese",
    "jw": "Javanese",
    "ka": "Georgian",
    "kk": "Kazakh",
    "km": "Khmer",
    "kn": "Kannada",
    "ko": "Korean",
    "la": "Latin",
    "lb": "Luxembourgish",
    "ln": "Lingala",
    "lo": "Lao",
    "lt": "Lithuanian",
    "lv": "Latvian",
    "mg": "Malagasy",
    "mi": "Maori",
    "mk": "Macedonian",
    "ml": "Malayalam",
    "mn": "Mongolian",
    "mr": "Marathi",
    "ms": "Malay",
    "mt": "Maltese",
    "my": "Myanmar",
    "ne": "Nepali",
    "nl": "Dutch",
    "nn": "Nynorsk",
    "no": "Norwegian",
    "oc": "Occitan",
    "pa": "Punjabi",
    "pl": "Polish",
    "ps": "Pashto",
    "pt": "Portuguese",
    "ro": "Romanian",
    "ru": "Russian",
    "sa": "Sanskrit",
    "sd": "Sindhi",
    "si": "Sinhala",
    "sk": "Slovak",
    "sl": "Slovenian",
    "sn": "Shona",
    "so": "Somali",
    "sq": "Albanian",
    "sr": "Serbian",
    "su": "Sundanese",
    "sv": "Swedish",
    "sw": "Swahili",
    "ta": "Tamil",
    "te": "Telugu",
    "tg": "Tajik",
    "th": "Thai",
    "tk": "Turkmen",
    "tl": "Tagalog",
    "tr": "Turkish",
    "tt": "Tatar",
    "uk": "Ukrainian",
    "ur": "Urdu",
    "uz": "Uzbek",
    "vi": "Vietnamese",
    "yi": "Yiddish",
    "yo": "Yoruba",
    "yue": "Cantonese",
    "zh": "Chinese",
}

# ─── Pares de tradução disponíveis no Argos Translate ──────────────────────
# Apenas pares cujo from_code existe no Whisper (garantia de uso real).
# Formato: (from_code, to_code) → (from_name, to_name)
# Pacotes são baixados automaticamente pelo TranslationEngine na primeira execução.
ARGOS_PAIRS: dict[tuple[str, str], tuple[str, str]] = {
    ("ar", "en"): ("Arabic",              "English"),
    ("az", "en"): ("Azerbaijani",         "English"),
    ("bg", "en"): ("Bulgarian",           "English"),
    ("bn", "en"): ("Bengali",             "English"),
    ("ca", "en"): ("Catalan",             "English"),
    ("cs", "en"): ("Czech",               "English"),
    ("da", "en"): ("Danish",              "English"),
    ("de", "en"): ("German",              "English"),
    ("el", "en"): ("Greek",               "English"),
    ("en", "ar"): ("English",             "Arabic"),
    ("en", "az"): ("English",             "Azerbaijani"),
    ("en", "bg"): ("English",             "Bulgarian"),
    ("en", "bn"): ("English",             "Bengali"),
    ("en", "ca"): ("English",             "Catalan"),
    ("en", "cs"): ("English",             "Czech"),
    ("en", "da"): ("English",             "Danish"),
    ("en", "de"): ("English",             "German"),
    ("en", "el"): ("English",             "Greek"),
    ("en", "eo"): ("English",             "Esperanto"),
    ("en", "es"): ("English",             "Spanish"),
    ("en", "et"): ("English",             "Estonian"),
    ("en", "eu"): ("English",             "Basque"),
    ("en", "fa"): ("English",             "Persian"),
    ("en", "fi"): ("English",             "Finnish"),
    ("en", "fr"): ("English",             "French"),
    ("en", "ga"): ("English",             "Irish"),
    ("en", "gl"): ("English",             "Galician"),
    ("en", "he"): ("English",             "Hebrew"),
    ("en", "hi"): ("English",             "Hindi"),
    ("en", "hu"): ("English",             "Hungarian"),
    ("en", "id"): ("English",             "Indonesian"),
    ("en", "it"): ("English",             "Italian"),
    ("en", "ja"): ("English",             "Japanese"),
    ("en", "ko"): ("English",             "Korean"),
    ("en", "ky"): ("English",             "Kyrgyz"),
    ("en", "lt"): ("English",             "Lithuanian"),
    ("en", "lv"): ("English",             "Latvian"),
    ("en", "ms"): ("English",             "Malay"),
    ("en", "nb"): ("English",             "Norwegian"),
    ("en", "nl"): ("English",             "Dutch"),
    ("en", "pb"): ("English",             "Portuguese (Brazil)"),
    ("en", "pl"): ("English",             "Polish"),
    ("en", "pt"): ("English",             "Portuguese"),
    ("en", "ro"): ("English",             "Romanian"),
    ("en", "ru"): ("English",             "Russian"),
    ("en", "sk"): ("English",             "Slovak"),
    ("en", "sl"): ("English",             "Slovenian"),
    ("en", "sq"): ("English",             "Albanian"),
    ("en", "sv"): ("English",             "Swedish"),
    ("en", "th"): ("English",             "Thai"),
    ("en", "tl"): ("English",             "Tagalog"),
    ("en", "tr"): ("English",             "Turkish"),
    ("en", "uk"): ("English",             "Ukrainian"),
    ("en", "ur"): ("English",             "Urdu"),
    ("en", "vi"): ("English",             "Vietnamese"),
    ("en", "zh"): ("English",             "Chinese"),
    ("en", "zt"): ("English",             "Chinese (Traditional)"),
    ("es", "en"): ("Spanish",             "English"),
    ("es", "pt"): ("Spanish",             "Portuguese"),
    ("et", "en"): ("Estonian",            "English"),
    ("eu", "en"): ("Basque",              "English"),
    ("fa", "en"): ("Persian",             "English"),
    ("fi", "en"): ("Finnish",             "English"),
    ("fr", "en"): ("French",              "English"),
    ("gl", "en"): ("Galician",            "English"),
    ("he", "en"): ("Hebrew",              "English"),
    ("hi", "en"): ("Hindi",               "English"),
    ("hu", "en"): ("Hungarian",           "English"),
    ("id", "en"): ("Indonesian",          "English"),
    ("it", "en"): ("Italian",             "English"),
    ("ja", "en"): ("Japanese",            "English"),
    ("ko", "en"): ("Korean",              "English"),
    ("lt", "en"): ("Lithuanian",          "English"),
    ("lv", "en"): ("Latvian",             "English"),
    ("ms", "en"): ("Malay",               "English"),
    ("nl", "en"): ("Dutch",               "English"),
    ("pl", "en"): ("Polish",              "English"),
    ("pt", "en"): ("Portuguese",          "English"),
    ("pt", "es"): ("Portuguese",          "Spanish"),
    ("ro", "en"): ("Romanian",            "English"),
    ("ru", "en"): ("Russian",             "English"),
    ("sk", "en"): ("Slovak",              "English"),
    ("sl", "en"): ("Slovenian",           "English"),
    ("sq", "en"): ("Albanian",            "English"),
    ("sv", "en"): ("Swedish",             "English"),
    ("th", "en"): ("Thai",                "English"),
    ("tl", "en"): ("Tagalog",             "English"),
    ("tr", "en"): ("Turkish",             "English"),
    ("uk", "en"): ("Ukrainian",           "English"),
    ("ur", "en"): ("Urdu",                "English"),
    ("vi", "en"): ("Vietnamese",          "English"),
    ("zh", "en"): ("Chinese",             "English"),
}


def is_pair_supported(from_code: str, to_code: str) -> bool:
    """Retorna True se o par (from_code, to_code) está disponível no Argos."""
    return (from_code, to_code) in ARGOS_PAIRS


def is_whisper_supported(lang_code: str) -> bool:
    """Retorna True se o idioma é reconhecido pelo Whisper."""
    return lang_code in WHISPER_LANGUAGES


def get_pair_names(from_code: str, to_code: str) -> tuple[str, str]:
    """Retorna (from_name, to_name) de um par suportado, ou usa o código como fallback."""
    pair = ARGOS_PAIRS.get((from_code, to_code))
    if pair:
        return pair
    from_name = WHISPER_LANGUAGES.get(from_code, from_code.upper())
    to_name = WHISPER_LANGUAGES.get(to_code, to_code.upper())
    return from_name, to_name


def print_supported_languages():
    """Imprime uma tabela formatada de idiomas e pares de tradução disponíveis."""
    print("\n" + "=" * 60)
    print("  IDIOMAS SUPORTADOS PARA TRANSCRICAO (Whisper)")
    print("=" * 60)
    codes = sorted(WHISPER_LANGUAGES.keys())
    for i in range(0, len(codes), 4):
        row = codes[i:i+4]
        print("  " + "   ".join(f"{c:<5} {WHISPER_LANGUAGES[c]:<18}" for c in row))

    print("\n" + "=" * 60)
    print("  PARES DISPONIVEIS PARA TRADUCAO (Argos Translate)")
    print("  (pacotes baixados automaticamente na 1a execucao)")
    print("=" * 60)
    for (fc, tc), (fn, tn) in sorted(ARGOS_PAIRS.items()):
        print(f"  --src {fc:<4} --tgt {tc:<4}  ({fn} -> {tn})")
    print()
