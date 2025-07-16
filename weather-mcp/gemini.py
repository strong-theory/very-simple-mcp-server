import os
import dotenv
from typing import Any
from google import genai
from google.genai import types
from mcp.client.stdio import stdio_client

dotenv.load_dotenv()


client = genai.Client(api_key=os.getenv("API_KEY"))


async def select_tool(prompt: str, mcp_tools: Any):
    tools = [
        types.Tool(
            function_declarations=[
                {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        k: v
                        for k, v in tool.inputSchema.items()
                        if k not in ["additionalProperties", "$schema"]
                    },
                }
            ]
        )
        for tool in mcp_tools
    ]
    # Remove debug prints

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0,
            tools=tools,
        ),
    )

    if response.candidates[0].content.parts[0].function_call:
        function_call = response.candidates[0].content.parts[0].function_call

        return {
            "name": function_call.name,
            "arguments": dict(function_call.args)
        }

    return {
        "error_message": response.candidates[0].content.parts[0].text
    }
    