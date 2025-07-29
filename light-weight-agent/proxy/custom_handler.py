import os, json, re, time, uuid, requests, httpx, litellm
from dotenv import load_dotenv
from litellm import CustomLLM, ModelResponse


class StackspotLLM(CustomLLM):
    def __init__(self):
        super().__init__()
        load_dotenv()
        self.client_id = os.getenv("STK_CLIENT_ID")
        self.client_secret = os.getenv("STK_CLIENT_SECRET")
        self.realm = os.getenv("REALM")
        self.genai_agent_id = os.getenv("GENAI_AGENT_ID")
        self.jwt = None
        

    def _convert_messages_to_prompt(self, messages, tools=None):
        """Convert OpenAI format messages to a custom prompt for Stackspot LLM"""
        prompt_parts = []

        # Add system instruction for tool usage
        if tools:
            tool_descriptions = []
            for tool in tools:
                func = tool.get("function", {})
                name = func.get("name", "")
                description = func.get("description", "")
                parameters = func.get("parameters", {})
                
                # Create a simplified parameter description
                param_desc = "No parameters required"
                if parameters and parameters.get("properties"):
                    param_list = []
                    for param_name, param_info in parameters["properties"].items():
                        param_type = param_info.get("type", "string")
                        param_desc_text = param_info.get("description", "")
                        required = param_name in parameters.get("required", [])
                        req_text = " (required)" if required else " (optional)"
                        param_list.append(f"  - {param_name} ({param_type}){req_text}: {param_desc_text}")
                    param_desc = "\n".join(param_list)
                
                tool_descriptions.append(f"Tool: {name}\nDescription: {description}\nParameters:\n{param_desc}")
            
            system_prompt = f"""You are a helpful AI assistant with access to tools that can help answer user questions.

                                IMPORTANT: When the user's request can be fulfilled by using one of the available tools, you MUST use the appropriate tool instead of providing your own answer.

                                Tool calling format - use EXACTLY this structure when calling a tool:
                                FUNCTION_CALL_START
                                tool_name_here
                                arguments: {{"parameter": "value"}}
                                FUNCTION_CALL_END

                                Available tools:
                                {chr(10).join(tool_descriptions)}

                                INSTRUCTIONS:
                                1. Analyze the user's request carefully
                                2. If any available tool can help answer the question, use that tool
                                3. Use the exact format shown above for tool calls
                                4. You can make multiple tool calls if needed
                                5. Wait for tool results before providing your final answer

                                Current conversation:"""
            prompt_parts.append(system_prompt)
        
        # Process conversation messages
        for msg in messages:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user":
                prompt_parts.append(f"\nUser: {content}")
            elif role == "assistant":
                if msg.get("tool_calls"):
                    # Handle assistant tool calls
                    prompt_parts.append("\nAssistant: I need to use some tools to help answer your question.")
                    for tool_call in msg["tool_calls"]:
                        func = tool_call.get("function", {})
                        name = func.get("name", "")
                        args = func.get("arguments", "{}")
                        prompt_parts.append(f"\nFUNCTION_CALL_START\nfunction_name: {name}\narguments: {args}\nFUNCTION_CALL_END")
                elif content:
                    prompt_parts.append(f"\nAssistant: {content}")
            elif role == "tool":
                # Handle tool results
                prompt_parts.append(f"\nTool Result: {content}")
        
        # Add final instruction
        if tools:
            prompt_parts.append(f"\n\nPlease analyze the user's request and use the appropriate tool if needed.")    
        
        return "".join(prompt_parts)

    def _detect_tool_calls(self, response_text):
        """Detect and parse tool calls from LLM response"""
        
        # Try multiple patterns to catch different formats
        patterns = [
            # Format from actual response: FUNCTION_CALL_START\nfunction_name\narguments: {...}\nFUNCTION_CALL_END
            r'FUNCTION_CALL_START\s*\n([^\n]+)\s*\narguments:\s*(\{.*?\})\s*\nFUNCTION_CALL_END',
            # New format: FUNCTION_CALL_START ... FUNCTION_CALL_END
            r'FUNCTION_CALL_START\s*\n?function_name:\s*([^\n]+)\s*\n?arguments:\s*(\{[^}]*\}|\[[^\]]*\]|[^\n]+)\s*\n?FUNCTION_CALL_END',
            # Old format: TOOL_CALL_START ... TOOL_CALL_END
            r'TOOL_CALL_START\s*(.*?)\s*TOOL_CALL_END',
            # Alternative JSON format
            r'\{\s*"function_name":\s*"([^"]+)"\s*,\s*"arguments":\s*(\{.*?\})\s*\}'
        ]
        
        tool_calls = []
        clean_response = response_text
        
        for pattern in patterns:
            matches = re.findall(pattern, response_text, re.DOTALL | re.IGNORECASE)
            
            if pattern == patterns[0]:  # Actual format from Stackspot
                for match in matches:
                    try:
                        function_name = match[0].strip()
                        arguments_str = match[1].strip()
                        
                        # Try to parse arguments as JSON
                        try:
                            arguments = json.loads(arguments_str)
                            # Remove extra Stackspot specific fields
                            clean_arguments = {}
                            for key, value in arguments.items():
                                if key not in ['step_id', 'tool_execution_id']:
                                    clean_arguments[key] = value
                            arguments = clean_arguments
                        except json.JSONDecodeError:
                            # If not JSON, treat as string or create simple object
                            if arguments_str.startswith('{') or arguments_str.startswith('['):
                                arguments = {"raw": arguments_str}
                            else:
                                arguments = {"value": arguments_str}
                        
                        tool_call = {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "type": "function",
                            "function": {
                                "name": function_name,
                                "arguments": json.dumps(arguments) if isinstance(arguments, dict) else str(arguments)
                            }
                        }
                        tool_calls.append(tool_call)
                        
                        # Remove this match from clean response
                        clean_response = re.sub(pattern, '', clean_response, flags=re.DOTALL | re.IGNORECASE)
                        
                    except Exception as e:
                        print(f"Error parsing tool call: {e}")
                        continue
                        
            elif pattern == patterns[1]:  # Format with function_name: prefix
                for match in matches:
                    try:
                        function_name = match[0].strip()
                        arguments_str = match[1].strip()
                        
                        # Try to parse arguments as JSON
                        try:
                            arguments = json.loads(arguments_str)
                        except json.JSONDecodeError:
                            # If not JSON, treat as string or create simple object
                            if arguments_str.startswith('{') or arguments_str.startswith('['):
                                arguments = {"raw": arguments_str}
                            else:
                                arguments = {"value": arguments_str}
                        
                        tool_call = {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "type": "function",
                            "function": {
                                "name": function_name,
                                "arguments": json.dumps(arguments) if isinstance(arguments, dict) else str(arguments)
                            }
                        }
                        tool_calls.append(tool_call)
                        
                        # Remove this match from clean response
                        clean_response = re.sub(pattern, '', clean_response, flags=re.DOTALL | re.IGNORECASE)
                        
                    except Exception as e:
                        print(f"Error parsing tool call: {e}")
                        continue
                        
            elif pattern == patterns[2]:  # Old format
                for match in matches:
                    try:
                        tool_data = json.loads(match.strip())
                        function_name = tool_data.get("function_name", "")
                        arguments = tool_data.get("arguments", {})
                        
                        tool_call = {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "type": "function",
                            "function": {
                                "name": function_name,
                                "arguments": json.dumps(arguments) if isinstance(arguments, dict) else str(arguments)
                            }
                        }
                        tool_calls.append(tool_call)
                        
                        clean_response = re.sub(pattern, '', clean_response, flags=re.DOTALL)
                        
                    except json.JSONDecodeError:
                        continue
            
            elif pattern == patterns[3]:  # Alternative JSON format
                for match in matches:
                    try:
                        function_name = match[0]
                        arguments = json.loads(match[1])
                        
                        tool_call = {
                            "id": f"call_{uuid.uuid4().hex[:8]}",
                            "type": "function",
                            "function": {
                                "name": function_name,
                                "arguments": json.dumps(arguments)
                            }
                        }
                        tool_calls.append(tool_call)
                        
                        clean_response = re.sub(pattern, '', clean_response, flags=re.DOTALL)
                        
                    except (json.JSONDecodeError, IndexError):
                        continue
        
        # Clean up the response
        clean_response = re.sub(r'FUNCTION_CALL_START.*?FUNCTION_CALL_END', '', clean_response, flags=re.DOTALL | re.IGNORECASE)
        clean_response = re.sub(r'TOOL_CALL_START.*?TOOL_CALL_END', '', clean_response, flags=re.DOTALL | re.IGNORECASE)
        clean_response = clean_response.strip()
        
        return tool_calls, clean_response

    def _format_openai_response(self, model, content, tool_calls=None):
        """Format response in OpenAI format"""
        response = ModelResponse(
            id=f"chatcmpl-{uuid.uuid4().hex[:8]}",
            created=int(time.time()),
            model=model,
            object="chat.completion",
            usage=litellm.Usage(
                prompt_tokens=0,  # You might want to calculate actual tokens
                completion_tokens=0,
                total_tokens=0
            ),
            choices=[
                litellm.Choices(
                    finish_reason="stop" if not tool_calls else "tool_calls",
                    index=0,
                    message=litellm.Message(
                        content=content if content.strip() and not tool_calls else None,
                        role="assistant",
                        tool_calls=tool_calls
                    )
                )
            ]
        )
        return response

    def authenticate(self):
        url = f"https://idm.stackspot.com/{self.realm}/oidc/oauth/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        resp = requests.post(url, data=data, headers=headers)
        resp.raise_for_status()
        self.jwt = resp.json()["access_token"]

    def completion(self, model, messages, **kwargs):
        if not self.jwt:
            self.authenticate()
        
        url = f"https://genai-inference-app.stackspot.com/v1/agent/{self.genai_agent_id}/chat"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jwt}"
        }
        
        # Extract tools from kwargs if provided
        tools = kwargs.get("tools", None)
        if tools is None:
            # Check if tools are in optional_params
            optional_params = kwargs.get("optional_params", {})
            tools = optional_params.get("tools", None)
        
        # Convert messages to custom prompt
        user_prompt = self._convert_messages_to_prompt(messages, tools)
        
        payload = {
            "streaming": False,
            "user_prompt": user_prompt,
            "stackspot_knowledge": False,
            "return_ks_in_response": False
        }

        # print(f"[DEBUG] Sending request to {url} with payload: {json.dumps(payload, indent=2)}")

        resp = requests.post(url, json=payload, headers=headers)
        print(f"[DEBUG] Response status: {resp.status_code}, content: {resp.text}")
        resp.raise_for_status()
        result = resp.json()
        content = result.get("message", "")
        
        # Detect tool calls in response
        tool_calls, clean_content = self._detect_tool_calls(content)
        
        # Format and return OpenAI-compatible response
        resposta = self._format_openai_response(model, clean_content, tool_calls)
        return resposta


    async def acompletion(self, model, messages, **kwargs):
        if not self.jwt:
            self.authenticate()
        
        url = f"https://genai-inference-app.stackspot.com/v1/agent/{self.genai_agent_id}/chat"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.jwt}"
        }
        
        # Extract tools from kwargs if provided
        tools = kwargs.get("tools", None)
        if tools is None:
            # Check if tools are in optional_params
            optional_params = kwargs.get("optional_params", {})
            tools = optional_params.get("tools", None)
        
        # Convert messages to custom prompt
        user_prompt = self._convert_messages_to_prompt(messages, tools)
        
        payload = {
            "streaming": False,  # Use non-streaming for async completion to get full response
            "user_prompt": user_prompt,
            "stackspot_knowledge": False,
            "return_ks_in_response": False
        }

        print(f"[DEBUG] Sending async request to {url} with payload: {json.dumps(payload, indent=2)}")

        async with httpx.AsyncClient(timeout=None) as client:
            resp = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            result = resp.json()
            content = result.get("message", "")
        
        # Detect tool calls in response
        tool_calls, clean_content = self._detect_tool_calls(content)
        
        # Format and return OpenAI-compatible response
        resp = self._format_openai_response(model, clean_content, tool_calls)
        print(f"[DEBUG] Async response: {resp}")
        return resp         

stackspot_llm = StackspotLLM()