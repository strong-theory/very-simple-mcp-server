import asyncio
from agents import Agent, OpenAIChatCompletionsModel, Runner, function_tool, set_tracing_disabled
from openai import AsyncOpenAI
import dotenv

MODEL_NAME="my-custom-llm/stackspot-chat"
BASE_URL= "http://localhost:4000/v1"


dotenv.load_dotenv()

@function_tool
def get_weather(city: str) -> str:
    return f"The weather in {city} is sunny."

client = AsyncOpenAI(api_key="dummy", base_url=BASE_URL)
set_tracing_disabled(disabled=True)

agent = Agent(
    name="Hello world",
    instructions="You are a helpful agent.",
    tools=[get_weather],
    model=OpenAIChatCompletionsModel(model=MODEL_NAME, openai_client=client),
)

async def main():
    result = await Runner.run(agent, input="What's the weather in Tokyo?")
    print(result.final_output)

if __name__ == "__main__":
    asyncio.run(main())