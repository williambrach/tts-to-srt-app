# tts-to-srt-app

A gradio-based application that converts text to speech using Azure OpenAI's TTS service (`gpt-4o-mini-tts`) and automatically generates SRT (`whisper`) subtitle files.

![image](/assets/example.png)

## Setup

.env
```
API_KEY=your_azure_openai_api_key
API_BASE=your_azure_openai_endpoint
```

.venv
```
curl -LsSf https://astral.sh/uv/install.sh | sh
uv venv --python 3.12
source .venv/bin/activate
uv sync
```

run
```
uv run python app.py
```

docker run
```
docker compose -f compose.yml up -d
```

## Usage

```
localhost:8888
```

