import os
import json
import dotenv
import requests
from pydantic import Field
from typing import Any, Dict, Iterator, List, Optional
from langchain_core.messages.ai import UsageMetadata
from langchain_core.language_models import BaseChatModel
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from langchain_core.messages import AIMessage, AIMessageChunk, BaseMessage, SystemMessage


dotenv.load_dotenv()


def get_token():
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "client_id": os.getenv("STK_CLIENT_ID"),
        "grant_type": "client_credentials",
        "client_secret": os.getenv("STK_CLIENT_SECRET"),
    }
    response = requests.post(os.getenv("STK_LOGIN_URL"), headers=headers, data=data)
    response.raise_for_status()
    return response.json().get("access_token")


def chat_stackspot_stream(user_prompt: str) -> Iterator[str]:
    headers = {
        "accept": "text/event-stream",
        "authorization": f"Bearer {get_token()}",
        "content-type": "application/json",
        "origin": "https://ai.stackspot.com",
        "user-agent": "Mozilla/5.0",
    }
    data = {
        "context": {
            "conversation_id": "01K0WRNY6C52GSMB57TXH4ASY3",
            "upload_ids": [],
            "agent_id": "01K0WRNZWSHAE5F1F1GBQJE6NN",
            "agent_built_in": False,
            "os": "Mozilla/5.0",
            "platform": "web-widget",
            "platform_version": "Mozilla/5.0",
            "stackspot_ai_version": "1.29.4",
        },
        "user_prompt": user_prompt,
    }
    response = requests.post(os.getenv("STK_AI_URL"), headers=headers, json=data, stream=True)
    response.raise_for_status()

    for line in response.iter_lines(decode_unicode=True):
        if line.startswith("data:"):
            data = line.removeprefix("data:").strip()
            if not data:
                continue
            json_data = json.loads(data)
            if "answer" in json_data:
                yield json_data["answer"]


class ChatStackSpot(BaseChatModel):
    """Custom LangChain-compatible model using StackSpot AI via streaming API."""

    model_name: str = Field(default="stackspot-ai")
    temperature: Optional[float] = None
    tools: Optional[List[Any]] = None  # Para armazenar as ferramentas vinculadas
    total_calls: int = 0

    def bind_tools(self, tools: List[Any], **kwargs: Any) -> "ChatStackSpot":
        """Vincula ferramentas ao modelo de chat."""
        self.tools = tools
        return self

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:

        if self.tools:
            tools_description = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
            system_message = SystemMessage(content=f"Você tem acesso às seguintes ferramentas:\n{tools_description}\nUse-as quando necessário.")
            messages = [system_message] + messages

        prompt = messages[-1].content if messages else ""

        chunks = list(chat_stackspot_stream(prompt))
        output = "".join(chunks)
        
        if self.total_calls >= 1:
            print("Returning cached response.")
            return ChatResult(
                generations=[
                    ChatGeneration(
                        generation_info={
                            'finish_reason': 'STOP',
                            'model_name': self.model_name,
                            'safety_ratings': []
                        },
                        message=AIMessage(
                            content=output,
                            additional_kwargs={},
                            response_metadata={},
                            tool_calls=[ ],
                            usage_metadata={
                                'input_tokens': 1,
                                'output_tokens': 0,
                                'total_tokens': 1,
                                'input_token_details': {'cache_read': 0}
                            }
                        )
                    )
                ],
                llm_output={'prompt_feedback': {'block_reason': 0, 'safety_ratings': []}}
            )
        self.total_calls += 1

        return ChatResult(
            generations=[
                ChatGeneration(
                    generation_info={'finish_reason': 'STOP', 'model_name': 'stackspot-ai', 'safety_ratings': []},
                    message=AIMessage(
                        content=output,
                        additional_kwargs={'function_call': {'name': 'download_open_api', 'arguments': '{"api_name": "AOtUo25GB3c"}'}},
                        response_metadata={},
                        tool_calls=[
                            {
                                'name': 'download_open_api',
                                'args': {'api_name': 'AOtUo25GB3c'},
                                'type': 'tool_call',
                                'id': 'tool-call-1',
                            }
                        ],
                        usage_metadata={'input_tokens': 1, 'output_tokens': 0, 'total_tokens': 1, 'input_token_details': {'cache_read': 0}}
                    )
                )
            ],
            llm_output={'prompt_feedback': {'block_reason': 0, 'safety_ratings': []}}
        )


    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        # Se houver ferramentas, adicionar uma descrição delas ao prompt
        if self.tools:
            tools_description = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
            system_message = SystemMessage(content=f"Você tem acesso às seguintes ferramentas:\n{tools_description}\nUse-as quando necessário.")
            messages = [system_message] + messages

        prompt = messages[-1].content if messages else ""

        input_tokens = sum(len(m.content) for m in messages)

        for token in chat_stackspot_stream(prompt):
            chunk = ChatGenerationChunk(
                message=AIMessageChunk(
                    content=token,
                    usage_metadata=UsageMetadata(
                        {
                            "input_tokens": input_tokens,
                            "output_tokens": 1,
                            "total_tokens": input_tokens + 1,
                        }
                    ),
                )
            )
            if run_manager:
                run_manager.on_llm_new_token(token, chunk=chunk)
            input_tokens = 0
            yield chunk

        yield ChatGenerationChunk(
            message=AIMessageChunk(
                content="",
                response_metadata={"model_name": self.model_name},
            )
        )

    @property
    def _llm_type(self) -> str:
        return "stackspot-ai"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        return {"model_name": self.model_name}