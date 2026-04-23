# 🎙️ Realtime Translation

Ferramenta de transcrição e tradução em tempo real do áudio do sistema (loopback), usando a biblioteca **RealtimeSTT** (com Whisper no backend) para reconhecimento de fala contínuo. Captura o que está sendo reproduzido pelo computador e exibe o conteúdo transcrevendo e traduzindo como uma legenda na tela — com baixíssima latência.

---

## ✨ Funcionalidades Atuais

- **Captura de áudio via Loopback (WASAPI)** — captura tudo que sai pelo dispositivo de saída padrão do Windows, sem necessidade de microfone, via `pyaudiowpatch`.
- **Transcrição Contínua (RealtimeSTT)** — streaming contínuo enviando pedaços de áudio e recebendo eventos de `on_realtime_text` e `on_final_text`.
- **Voice Activity Detection (VAD Inteligente)** — o Silero VAD (embutido no RealtimeSTT) isola a fala do silêncio, emitindo contexto perfeitamente cortado.
- **Suporte Multi-Idioma e Tradução Offline** — uso do **Argos Translate** para converter texto (ex: Inglês para Português) on-the-fly, sincronizado com o streaming de áudio. Suporta dezenas de pares de idiomas via linha de comando com download automático de pacotes.
- **Overlay Flutuante na Tela** — as legendas aparecem em uma janela transparente que sobrepõe outras aplicações de forma indolor e limpa (ideal para vídeos ou reuniões).
- **Graceful Shutdown** — Gerenciamento adequado do ciclo de vida das threads para encerramentos seguros sem estourar pipelines do loop principal do sistema.

---

## 🗂️ Estrutura do Projeto

```
realtime_translation/
├── main.py                  # Ponto de entrada da aplicação (gerencia STT, Treads e UI)
├── requirements.txt         # Dependências do projeto
│
├── config/
│   └── languages.py         # Catálogo validado de idiomas (Whisper) e pares de tradução (Argos)
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

### Executando e Configurando

A aplicação agora é configurada via **argumentos de linha de comando** (CLI).

**Comando Padrão (Inglês → Português com modelo `base`):**
```bash
python main.py
```

**Exemplos de uso avançado:**
```bash
# Traduzir de Espanhol para Português
python main.py --src es --tgt pt

# Traduzir de Inglês para Japonês usando o modelo Whisper 'small'
python main.py --src en --tgt ja --model small

# Modo apenas transcrição (sem tradução, exibe legenda na língua original)
python main.py --src en --no-translate

# Listar todos os idiomas de origem e pares de tradução suportados
python main.py --list-langs
```

| Argumento | Atalho | Padrão | Descrição |
|---|---|---|---|
| `--src` | `-s` | `en` | Código do idioma de origem (ex: `en`, `es`, `fr`). Usa os códigos suportados pelo Whisper. |
| `--tgt` | `-t` | `pt` | Código do idioma de destino (ex: `pt`, `en`, `ja`). Os pacotes são baixados do Argos Translate automaticamente. |
| `--model` | `-m` | `base` | Tamanho do modelo Whisper (`tiny`, `base`, `small`, `medium`, `large`, `large-v2`, `large-v3`). |
| `--no-translate` | | | Desativa o motor de tradução. O overlay exibirá o texto original transcrito. |
| `--list-langs` | | | Imprime a tabela completa de idiomas suportados no terminal e encerra a aplicação. |

O programa irá:
1. Detectar o dispositivo de reprodução de áudio padrão (loopback).
2. Validar os idiomas solicitados e baixar os modelos de tradução necessários (apenas na 1ª vez).
3. Carregar o modelo STT e abrir o overlay transparente da interface gráfica (agora com um discreto indicador de idioma).
4. Processar o áudio via background thread e exibir as legendas.

Pressione `Ctrl+C` no terminal ou simplesmente feche a janela do overlay para encerrar a aplicação.

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
- [x] **Seleção de idioma de origem e destino** via interface ou configuração (implementado via CLI arguments).
- [ ] **Interface gráfica (GUI)** — controles expandidos na própria janela para alternar modelos on-the-fly.
- [ ] **Histórico de transcrições** — salvar transcrições em arquivo de texto.
