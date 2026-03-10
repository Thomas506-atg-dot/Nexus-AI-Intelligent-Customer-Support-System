# Academic AI Assistant

An AI assistant focused exclusively on academic use: research, study, writing, and citations.

## Features

- **Concept explanation** – Clear explanations with examples
- **Research support** – Research questions, literature search, methodologies
- **Academic writing** – Structure essays, feedback on clarity and argumentation
- **Study assistance** – Summaries, step-by-step solutions, revision support
- **Citation guidance** – APA, MLA, Chicago formatting help
- **Critical thinking** – Analysis, source evaluation, argumentation support

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure your AI provider

Copy the example config and edit it:

```bash
cp .env.example .env
```

**Option A: OpenAI** (requires API key)

- Set `AI_PROVIDER=openai`
- Add your key: `OPENAI_API_KEY=sk-...`
- Get a key at [platform.openai.com](https://platform.openai.com/api-keys)

**Option B: Ollama** (local, free)

- Install [Ollama](https://ollama.ai)
- Run a model: `ollama run llama3.2`
- Set `AI_PROVIDER=ollama` in `.env`

### 3. Run the app

```bash
streamlit run app.py
```

Open the URL shown in the terminal (usually http://localhost:8501).

## Environment variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AI_PROVIDER` | `openai` or `ollama` | `openai` |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o-mini` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` |
| `OLLAMA_MODEL` | Ollama model name | `llama3.2` |

## Academic integrity

This assistant is meant to support learning and research. It is not designed to:

- Write full essays or papers for you
- Help with exam cheating
- Facilitate plagiarism

Use it to understand concepts, improve structure, and strengthen your own arguments.
