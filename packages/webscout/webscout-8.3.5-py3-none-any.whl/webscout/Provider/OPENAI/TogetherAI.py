from typing import List, Dict, Optional, Union, Generator, Any

from webscout.Provider.OPENAI.base import OpenAICompatibleProvider, BaseChat, BaseCompletions
from webscout.Provider.OPENAI.utils import (
    ChatCompletionChunk, ChatCompletion, Choice, ChoiceDelta,
    ChatCompletionMessage, CompletionUsage, count_tokens
)

import requests
import uuid
import time
import json
from webscout.litagent import LitAgent

class Completions(BaseCompletions):
    def __init__(self, client: 'TogetherAI'):
        self._client = client

    def create(
        self,
        *,
        model: str,
        messages: List[Dict[str, str]],
        max_tokens: Optional[int] = None,
        stream: bool = False,
        temperature: Optional[float] = None,
        top_p: Optional[float] = None,
        timeout: Optional[int] = None,
        proxies: Optional[Dict[str, str]] = None,
        stop: Optional[Union[str, List[str]]] = None,
        **kwargs: Any
    ) -> Union[ChatCompletion, Generator[ChatCompletionChunk, None, None]]:
        """
        Creates a model response for the given chat conversation.
        Mimics openai.chat.completions.create
        """
        # Get API key if not already set
        if not self._client.headers.get("Authorization"):
            api_key = self._client.get_activation_key()
            self._client.headers["Authorization"] = f"Bearer {api_key}"
            self._client.session.headers.update(self._client.headers)

        model_name = self._client.convert_model_name(model)
        payload = {
            "model": model_name,
            "messages": messages,
            "stream": stream,
        }
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens
        if temperature is not None:
            payload["temperature"] = temperature
        if top_p is not None:
            payload["top_p"] = top_p
        if stop is not None:
            payload["stop"] = stop
        payload.update(kwargs)

        request_id = f"chatcmpl-{uuid.uuid4()}"
        created_time = int(time.time())

        if stream:
            return self._create_stream(request_id, created_time, model_name, payload, timeout, proxies)
        else:
            return self._create_non_stream(request_id, created_time, model_name, payload, timeout, proxies)

    def _create_stream(
        self, request_id: str, created_time: int, model: str, payload: Dict[str, Any], timeout: Optional[int] = None, proxies: Optional[Dict[str, str]] = None
    ) -> Generator[ChatCompletionChunk, None, None]:
        try:
            response = self._client.session.post(
                self._client.api_endpoint,
                headers=self._client.headers,
                json=payload,
                stream=True,
                timeout=timeout or self._client.timeout,
                proxies=proxies
            )
            response.raise_for_status()
            prompt_tokens = count_tokens([msg.get("content", "") for msg in payload.get("messages", [])])
            completion_tokens = 0
            total_tokens = prompt_tokens
            
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith('data: '):
                        line = line[6:]
                        if line.strip() == '[DONE]':
                            break
                        try:
                            chunk_data = json.loads(line)
                            if 'choices' in chunk_data and chunk_data['choices']:
                                delta = chunk_data['choices'][0].get('delta', {})
                                content = delta.get('content')
                                if content:
                                    completion_tokens += count_tokens(content)
                                    total_tokens = prompt_tokens + completion_tokens
                                    choice_delta = ChoiceDelta(
                                        content=content,
                                        role=delta.get('role', 'assistant'),
                                        tool_calls=delta.get('tool_calls')
                                    )
                                    choice = Choice(
                                        index=0,
                                        delta=choice_delta,
                                        finish_reason=None,
                                        logprobs=None
                                    )
                                    chunk = ChatCompletionChunk(
                                        id=request_id,
                                        choices=[choice],
                                        created=created_time,
                                        model=model
                                    )
                                    chunk.usage = {
                                        "prompt_tokens": prompt_tokens,
                                        "completion_tokens": completion_tokens,
                                        "total_tokens": total_tokens,
                                        "estimated_cost": None
                                    }
                                    yield chunk
                        except Exception:
                            continue
            
            # Final chunk with finish_reason="stop"
            delta = ChoiceDelta(content=None, role=None, tool_calls=None)
            choice = Choice(index=0, delta=delta, finish_reason="stop", logprobs=None)
            chunk = ChatCompletionChunk(
                id=request_id,
                choices=[choice],
                created=created_time,
                model=model
            )
            chunk.usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "total_tokens": total_tokens,
                "estimated_cost": None
            }
            yield chunk
        except Exception as e:
            raise IOError(f"TogetherAI stream request failed: {e}") from e

    def _create_non_stream(
        self, request_id: str, created_time: int, model: str, payload: Dict[str, Any], timeout: Optional[int] = None, proxies: Optional[Dict[str, str]] = None
    ) -> ChatCompletion:
        try:
            payload_copy = payload.copy()
            payload_copy["stream"] = False
            response = self._client.session.post(
                self._client.api_endpoint,
                headers=self._client.headers,
                json=payload_copy,
                timeout=timeout or self._client.timeout,
                proxies=proxies
            )
            response.raise_for_status()
            data = response.json()
            
            full_text = ""
            finish_reason = "stop"
            if 'choices' in data and data['choices']:
                full_text = data['choices'][0]['message']['content']
                finish_reason = data['choices'][0].get('finish_reason', 'stop')
            
            message = ChatCompletionMessage(
                role="assistant",
                content=full_text
            )
            choice = Choice(
                index=0,
                message=message,
                finish_reason=finish_reason
            )
            
            prompt_tokens = count_tokens([msg.get("content", "") for msg in payload.get("messages", [])])
            completion_tokens = count_tokens(full_text)
            usage = CompletionUsage(
                prompt_tokens=prompt_tokens,
                completion_tokens=completion_tokens,
                total_tokens=prompt_tokens + completion_tokens
            )
            
            completion = ChatCompletion(
                id=request_id,
                choices=[choice],
                created=created_time,
                model=model,
                usage=usage,
            )
            return completion
        except Exception as e:
            raise IOError(f"TogetherAI non-stream request failed: {e}") from e


class Chat(BaseChat):
    def __init__(self, client: 'TogetherAI'):
        self.completions = Completions(client)


class TogetherAI(OpenAICompatibleProvider):
    """
    OpenAI-compatible client for TogetherAI API.
    """
    AVAILABLE_MODELS = [
        "mistralai/Mistral-7B-Instruct-v0.3",
        "togethercomputer/MoA-1",
        "Qwen/Qwen2.5-7B-Instruct-Turbo",
        "meta-llama/Llama-3-8b-chat-hf",
        "meta-llama/Meta-Llama-3.1-405B-Instruct-Turbo",
        "togethercomputer/MoA-1-Turbo",
        "eddiehou/meta-llama/Llama-3.1-405B",
        "mistralai/Mistral-7B-Instruct-v0.2",
        "meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        "meta-llama/Llama-3.2-11B-Vision-Instruct-Turbo",
        "meta-llama/Meta-Llama-3-70B-Instruct-Turbo",
        "meta-llama/Llama-3.3-70B-Instruct-Turbo",
        "Qwen/Qwen2.5-VL-72B-Instruct",
        "arcee-ai/AFM-4.5B-Preview",
        "lgai/exaone-3-5-32b-instruct",
        "meta-llama/Llama-3-70b-chat-hf",
        "mistralai/Mixtral-8x7B-Instruct-v0.1",
        "google/gemma-2-27b-it",
        "Qwen/Qwen2-72B-Instruct",
        "mistralai/Mistral-Small-24B-Instruct-2501",
        "Qwen/Qwen2-VL-72B-Instruct",
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-1.5B",
        "meta-llama/Llama-Vision-Free",
        "perplexity-ai/r1-1776",
        "scb10x/scb10x-llama3-1-typhoon2-70b-instruct",
        "arcee-ai/maestro-reasoning",
        "togethercomputer/Refuel-Llm-V2-Small",
        "Qwen/Qwen2.5-Coder-32B-Instruct",
        "arcee-ai/coder-large",
        "Qwen/QwQ-32B",
        "arcee_ai/arcee-spotlight",
        "deepseek-ai/DeepSeek-R1-0528-tput",
        "marin-community/marin-8b-instruct",
        "lgai/exaone-deep-32b",
        "google/gemma-3-27b-it",
        "deepseek-ai/DeepSeek-R1-Distill-Llama-70B",
        "NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO",
        "mistralai/Mistral-7B-Instruct-v0.1",
        "meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        "deepseek-ai/DeepSeek-R1-Distill-Qwen-14B",
        "deepseek-ai/DeepSeek-R1-Distill-Llama-70B-free",
        "scb10x/scb10x-typhoon-2-1-gemma3-12b",
        "togethercomputer/Refuel-Llm-V2",
        "Qwen/Qwen2.5-72B-Instruct-Turbo",
        "meta-llama/Meta-Llama-3-8B-Instruct-Lite",
        "meta-llama/Llama-4-Scout-17B-16E-Instruct",
        "meta-llama/Llama-3.2-3B-Instruct-Turbo",
        "nvidia/Llama-3.1-Nemotron-70B-Instruct-HF",
        "deepseek-ai/DeepSeek-V3",
        "Qwen/Qwen3-Coder-480B-A35B-Instruct-FP8",
        "meta-llama/Meta-Llama-3.1-70B-Instruct-Turbo",
        "Qwen/Qwen3-32B-FP8",
        "meta-llama/Llama-3.2-90B-Vision-Instruct-Turbo",
        "arcee-ai/virtuoso-large",
        "google/gemma-3n-E4B-it",
        "moonshotai/Kimi-K2-Instruct",
        "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "deepseek-ai/DeepSeek-R1",
        "Qwen/Qwen3-235B-A22B-fp8-tput",
        "Qwen/Qwen3-235B-A22B-Instruct-2507-tput",
        "Rrrr/nim/nvidia/llama-3.3-nemotron-super-49b-v1-de6a6453",
        "Rrrr/mistralai/Devstral-Small-2505-306f5881",
        "Qwen/Qwen3-235B-A22B-Thinking-2507",
        "Rrrr/ChatGPT-5",
        "Rrrr/MeowGPT-3.5",
        "blackbox/meta-llama-3-1-8b"
    ]

    def __init__(self, browser: str = "chrome"):
        self.timeout = 60
        self.api_endpoint = "https://api.together.xyz/v1/chat/completions"
        self.activation_endpoint = "https://www.codegeneration.ai/activate-v2"
        self.session = requests.Session()
        self.headers = LitAgent().generate_fingerprint(browser=browser)
        self.session.headers.update(self.headers)
        self.chat = Chat(self)
        self._api_key_cache = None

    @property
    def models(self):
        class _ModelList:
            def list(inner_self):
                return TogetherAI.AVAILABLE_MODELS
        return _ModelList()

    def get_activation_key(self) -> str:
        """Get API key from activation endpoint"""
        if self._api_key_cache:
            return self._api_key_cache
            
        try:
            response = requests.get(
                self.activation_endpoint,
                headers={"Accept": "application/json"},
                timeout=30
            )
            response.raise_for_status()
            activation_data = response.json()
            self._api_key_cache = activation_data["openAIParams"]["apiKey"]
            return self._api_key_cache
        except Exception as e:
            raise Exception(f"Failed to get activation key: {e}")

    def convert_model_name(self, model: str) -> str:
        """Convert model name - returns model if valid, otherwise default"""
        if model in self.AVAILABLE_MODELS:
            return model
        
        # Default to first available model if not found
        return self.AVAILABLE_MODELS[0]


if __name__ == "__main__":
    from rich import print
    
    client = TogetherAI()
    messages = [
        {"role": "user", "content": "Hello, how are you?"},
        {"role": "assistant", "content": "I'm fine, thank you! How can I help you today?"},
        {"role": "user", "content": "Tell me a short joke."}
    ]
    
    # Non-streaming example
    response = client.chat.completions.create(
        model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages=messages,
        max_tokens=50,
        stream=False
    )
    print("Non-streaming response:")
    print(response)
    
    # Streaming example
    print("\nStreaming response:")
    stream = client.chat.completions.create(
        model="meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8",
        messages=messages,
        max_tokens=50,
        stream=True
    )
    
    for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="")
    print()