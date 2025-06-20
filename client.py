import asyncio
from gemini import select_tool
from fastmcp import Client, FastMCP


config = {
    "mcpServers": {
        "clima": {
            "url": "http://localhost:9000/weather",
            "transport": "streamable-http"
        }
    }
}

client = Client(config)

async def main():
    async with client:

        available_tools = await client.list_tools()

        query = input("Digite sua pergunta: ")

        selected_tool = await select_tool(query, available_tools)

        if"error_message" in selected_tool.keys():
            print("Error selecting tool:", selected_tool["error_message"])
            return

        print("Selected tool:", selected_tool["name"])

        weather_data = await client.call_tool(selected_tool["name"], selected_tool["arguments"])

        print(f"{query}:\n", weather_data[0].text)
        
        

if __name__ == "__main__":
    asyncio.run(main())
