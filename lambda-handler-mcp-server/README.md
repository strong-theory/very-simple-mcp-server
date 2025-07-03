## Lambda to handle mcp server

Source: [mcp-lambda-handler](https://github.com/awslabs/mcp/tree/main/src/mcp-lambda-handler)


## Running

```shell
python3 -m venv .venv

source .venv/bin/activate

python3 -m pip install -r requirements.txt

python3 server.py
```


## Packing a layer

```shell
pip install -r requirements.txt -t python/
zip -r python.zip python/
``` 