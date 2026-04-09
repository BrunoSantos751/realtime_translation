# 🎙️ Realtime Translation

Ferramenta de transcrição e tradução em tempo real do áudio do sistema (loopback), usando a biblioteca **RealtimeSTT** (com Whisper no backend) para reconhecimento de fala contínuo. Captura o que está sendo reproduzido pelo computador e exibe o conteúdo transcrevendo e traduzindo como uma legenda na tela — com baixíssima latência.

---

## ✨ Funcionalidades Atuais

- **Captura de áudio via Loopback (WASAPI)** — captura tudo que sai pelo dispositivo de saída padrão do Windows, sem necessidade de microfone, via `pyaudiowpatch`.
- **Transcrição Contínua (RealtimeSTT)** — streaming contínuo enviando pedaços de áudio e recebendo eventos de `on_realtime_text` e `on_final_text`.
- **Voice Activity Detection (VAD Inteligente)** — o Silero VAD (embutido no RealtimeSTT) isola a fala do silêncio, emitindo contexto perfeitamente cortado.
- **Tradução Offline Incremental** — uso do **Argos Translate** para converter texto de Inglês para Português on-the-fly, sincronizado com os retornos streaming de áudio.
- **Overlay Flutuante na Tela** — as legendas aparecem em uma janela transparente que sobrepõe outras aplicações de forma indolor e limpa (ideal para vídeos ou reuniões).
- **Graceful Shutdown** — Gerenciamento adequado do ciclo de vida das threads para encerramentos seguros sem estourar pipelines do loop principal do sistema.

---

## 🗂️ Estrutura do Projeto

```
realtime_translation/
├── main.py                  # Ponto de entrada da aplicação (gerencia STT, Treads e UI)
├── requirements.txt         # Dependências do projeto
│
├── audio/
│   ├── capture.py           # Captura de áudio loopback (WASAPI)
│   └── preprocess.py        # Conversão, mixagem, reamostragem (float32 para int16)
│
├── speech/
│   └── realtimestt_engine.py # Wrapper do RealtimeSTT conectando callbacks
│
├── translation/
│   └── translator.py        # Módulo de tradução offline com Argos Translate
├── overlay/                 
│   └── subtitle_window.py   # Interface gráfica (Overlay) baseada em Tkinter
│
└── tests/
    └── test_audio_buffer.py # Scripts e testes legados
```

---

## 🚀 Como Usar

### Pré-requisitos

- Windows 10/11
- Python 3.10+

### Instalação

```bash
# Clone o repositório
git clone https://github.com/BrunoSantos751/realtime_translation.git
cd realtime_translation

# Instale as dependências
pip install -r requirements.txt
```

> **Nota:** Instale o FFmpeg no sistema ou utilizando um gerenciador de pacotes como `winget install ffmpeg`.

### Executando

```bash
python main.py
```

O programa irá:
1. Detectar o dispositivo de reprodução de áudio padrão (loopback).
2. Carregar o modelo RealtimeSTT na memória (configurado como `base` por padrão).
3. Abrir o overlay transparente da interface gráfica.
4. Escutar e processar o áudio do computador via background thread, jogando as legendas em PT-BR para a tela.

Pressione `Ctrl+C` no terminal ou simplesmente feche a janela do overlay para encerrar a aplicação com segurança.

### Configuração

No `main.py`, você pode ajustar alguns parâmetros base modificando as linhas:

| Parâmetro | Onde | Descrição |
|---|---|---|
| `model_name` | `RealtimeSTTTranscriber(model_name=...)` | Modelo STT de reconhecimento: `tiny`, `base`, `small`, `medium`, `large` |
| `chunk_duration` | `capturer.start_capture(...)` | Duração do buffer de gravação rápida (ex.: `0.15s` garante alta reatividade) |
| `from_code` / `to_code` | Dentro de `TranslationEngine(...)` | Idiomas de origem e destino da tradução via Argos Translate |

---

## 📦 Dependências

| Pacote | Função |
|---|---|
| `pyaudiowpatch` | Captura de áudio loopback via WASAPI no Windows excluso para loopbacks de áudio |
| `RealtimeSTT` | Engine de reconhecimento de voz baseada em Whisper otimizada para tempo real e streaming |
| `argostranslate` | Tradução local e offline que preserva a privacidade e velocidade |
| `numpy` / `scipy` | Processamento matemático do áudio cru |

---

## 🗺️ Roadmap

- [x] **Módulo de Tradução offline** — traduzindo transcrições com algoritmos anti-repetição usando Argos Translate.
- [x] **Overlay na Tela** — exibição do texto transcrito/traduzido como uma janela flutuante transparente sobre outras aplicações (ideal para lives, videoconferências e conteúdo em língua estrangeira).
- [ ] **Seleção de idioma de origem e destino** via interface ou configuração.
- [ ] **Interface gráfica (GUI)** — controles expandidos na própria janela para alternar modelos on-the-fly.
- [ ] **Histórico de transcrições** — salvar transcrições em arquivo de texto.
