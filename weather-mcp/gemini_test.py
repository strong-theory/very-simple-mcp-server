import asyncio
from gemini import select_tool

query = "Qual o clima em São Paulo?"

tools = [
    {
        "name": "weather", 
        "description": "Consulta o clima atual informando apenas o nome da cidade.\\n    Exemplo: clima(\"São Paulo\")\\n    ",
        "inputSchema": {'properties': {'city': {'title': 'City', 'type': 'string'}}, 'required': ['city'], 'type': 'object'},
        "annotations": None
    }
]


asyncio.run(select_tool(query, tools))