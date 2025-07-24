import asyncio
from llm import ChatStackSpot
from dotenv import load_dotenv
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

load_dotenv()


@tool
def download_open_api(api_name: str) -> str:
    """Download the OpenAPI specification for a given API name. and return its content."""
    with open("./openapi.json", "r") as file:
        return file.read()
    return "text"


async def main():
    tools = [download_open_api]
    model = ChatStackSpot(tools=tools, streaming=False)
    model = model.bind_tools(tools)
    agent = create_react_agent(model, tools)

    messages = [
        {
            "role": "system",
            "content": "You are a helpful assistant that can summary the youtube's video transcriptions. Think step by step and use the appropriate tools to help the user."
        }
    ]

    print("Available Tools -", *[tool.name for tool in tools])
    print("-" * 60)

    while True:
        user_input = input("\nYou: ")
        if user_input == "quit":
            print("Goodbye")
            break

        messages.append({"role": "user", "content": user_input[:175000]})

        try:
            agent_response = agent.invoke({"messages": messages})

            ai_message = agent_response["messages"][-1].content
            print("\nAgent:", ai_message)
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())
# from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

# response = model.invoke([HumanMessage(content="Olá, tudo bem?")])
# print(response.content)
