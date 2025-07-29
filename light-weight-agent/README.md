## light-weight-agent

** proxy **

```shell
cd proxy
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
litellm --config config.yaml --port 4000
```


** app **

```shell
cd app
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
python3 agent.py
```