# 🎙️ Realtime Translation

Ferramenta de transcrição e tradução em tempo real do áudio do sistema (loopback), usando **OpenAI Whisper** para reconhecimento de fala. Captura o que está sendo reproduzido pelo computador e transcreve o conteúdo diretamente no terminal — com baixíssima latência.

---

## ✨ Funcionalidades Atuais

- **Captura de áudio via Loopback (WASAPI)** — captura tudo que sai pelo dispositivo de saída padrão do Windows, sem necessidade de microfone.
- **Buffer contínuo (Rolling Buffer)** — gerencia ativamente o fluxo de áudio, evitando acúmulo e latência progressiva.
- **Pré-processamento de áudio** — converte para `float32`, mixagem stereo→mono e reamostragem para 16 kHz (padrão do Whisper).
- **VAD simples (Voice Activity Detection)** — ignora silêncio com base em limiar de energia RMS, evitando transcrições vazias.
- **Transcrição via OpenAI Whisper** — suporte a múltiplos modelos (`tiny`, `base`, `small`, `medium`, `large`) com aceleração GPU instantânea via CUDA.
- **Tradução Offline Incremental** — uso do **Argos Translate** para converter texto de Inglês para Português, analisando apenas o delta das palavras novas, evitando repetição de texto já traduzido.
- **Captura em thread separada** — o processamento principal não bloqueia a captura de áudio.

---

## 🗂️ Estrutura do Projeto

```
realtime_translation/
├── main.py                  # Ponto de entrada da aplicação
├── requirements.txt         # Dependências do projeto
│
├── audio/
│   ├── capture.py           # Captura de áudio loopback (WASAPI) com buffer circular
│   └── preprocess.py        # Conversão, mixagem, reamostragem e VAD
│
├── speech/
│   └── whisper_engine.py    # Wrapper do OpenAI Whisper para transcrição
│
├── pipeline/
│   └── rolling_buffer.py    # Buffer contínuo para evitar latência cumulativa
├── translation/
│   └── translator.py        # Módulo de tradução offline com Argos Translate
├── overlay/                 # (futuro) Overlay na tela
│
└── tests/
    ├── test_audio_buffer.py      # Testes do buffer de áudio
    └── test_resample_speed.py    # Benchmark de reamostragem
```

---

## 🚀 Como Usar

### Pré-requisitos

- Windows 10/11
- Python 3.10+
- PyTorch instalado (com suporte a CUDA opcional, para GPU)

### Instalação

```bash
# Clone o repositório
git clone https://github.com/BrunoSantos751/realtime_translation.git
cd realtime_translation

# Instale as dependências
pip install -r requirements.txt
```

> **Nota:** O `openai-whisper` requer `ffmpeg` instalado no sistema. Instale via [ffmpeg.org](https://ffmpeg.org/download.html) ou com `winget install ffmpeg`.

### Executando

```bash
python main.py
```

O programa irá:
1. Detectar automaticamente o dispositivo de saída padrão (loopback).
2. Carregar o modelo Whisper (`small` por padrão) e o modelo de tradução do Argos Translate (baixa automaticamente no primeiro uso).
3. Iniciar a captura de áudio, executando VAD, transcrição em Inglês e tradução inteligente para o Português em tempo real no terminal.

Pressione `Ctrl+C` para encerrar.

### Configuração

No `main.py`, você pode ajustar:

| Parâmetro | Onde | Descrição |
|---|---|---|
| `model_name` | `WhisperTranscriber(model_name=...)` | Modelo Whisper: `tiny`, `base`, `small`, `medium`, `large` |
| `chunk_duration` | `capturer.start_capture(...)` | Duração da captura rápida de cada chunk em segundos (ex: `0.4s`) |
| `language` | `transcriber.transcribe(..., language=...)` | Idioma de *origem* capturado no áudio, ex: `"en"` |
| `window_size` | `RollingAudioBuffer(window_size=...)` | Tamanho da janela enviada ao Whisper (padrão: `2.5s`) |
| `from_code` / `to_code` | `TranslationEngine(from_code=..., to_code=...)` | Idiomas de tradução, do Argos Translate (ex: `"en"` para `"pt"`) |

---

## 📦 Dependências

| Pacote | Função |
|---|---|
| `pyaudiowpatch` | Captura de áudio loopback via WASAPI no Windows |
| `openai-whisper` | Modelo de reconhecimento de fala |
| `torch` | Backend para execução do Whisper (CPU ou GPU) |
| `numpy` | Manipulação de arrays de áudio |
| `scipy` | Reamostragem de áudio |
| `argostranslate` | Tradução local offline |

---

## 🗺️ Roadmap

- [x] **Módulo de Tradução offline** — traduzindo transcrições com algoritmos anti-repetição usando Argos Translate.
- [ ] **Overlay na Tela** — exibição do texto transcrito/traduzido como uma janela flutuante transparente sobre outras aplicações (ideal para lives, videoconferências e conteúdo em língua estrangeira).
- [ ] **Seleção de idioma de origem e destino** via interface ou configuração.
- [ ] **Interface gráfica (GUI)** — controles para iniciar/parar, selecionar modelo e idioma.
- [ ] **Histórico de transcrições** — salvar transcrições em arquivo de texto.

