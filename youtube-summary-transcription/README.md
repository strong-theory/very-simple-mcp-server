## youtube-summary-transcription

MCP Server with tools to download a transcription from a youtube video and make a summary and a markdown documentation.

It also includes a CLI agent.

### Setup the project

1. Install the dependencies

```shell
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

2. Setup .env file with your gemini key

```properties
GOOGLE_API_KEY=CONFIGURE_YOUR_GEMINI_KEY
```

### Running the server

```shell
python3 server.py
```

### Running the agent

```shell
python3 agent.py
```

Usage the agent, ask for

```
Create a documentation from the video https://www.youtube.com/watch?v=AOtUo25GB3c
```