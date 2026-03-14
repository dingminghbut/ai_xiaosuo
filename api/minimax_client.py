"""MiniMax API client."""

import json
import time
from typing import Generator, Optional
import requests

from ai_xiaosuo.config import (
    MINIMAX_API_KEY,
    MINIMAX_BASE_URL,
    MINIMAX_MODEL,
    API_TIMEOUT,
    API_MAX_RETRIES,
    API_RETRY_DELAY,
    TOKEN_COST_INPUT,
    TOKEN_COST_OUTPUT,
)


class MiniMaxClient:
    """Client for MiniMax API."""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the MiniMax client.
        
        Args:
            api_key: MiniMax API key. If not provided, uses config value.
        """
        self.api_key = api_key or MINIMAX_API_KEY
        self.base_url = MINIMAX_BASE_URL
        self.model = MINIMAX_MODEL
        self.timeout = API_TIMEOUT
        self.max_retries = API_MAX_RETRIES
        self.retry_delay = API_RETRY_DELAY
        
    def _estimate_tokens(self, text: str) -> int:
        """Estimate token count for text (rough approximation)."""
        # Rough estimation: 1 token ≈ 1.5 Chinese characters or 4 English words
        chinese_chars = sum(1 for c in text if '\u4e00' <= c <= '\u9fff')
        english_words = len(text.split()) - chinese_chars
        return int(chinese_chars / 1.5 + english_words / 4)
    
    def _call_api(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4000,
        stream: bool = False,
    ) -> dict:
        """Call MiniMax API.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            stream: Whether to use streaming
            
        Returns:
            API response dict
        """
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }
        
        for attempt in range(self.max_retries):
            try:
                response = requests.post(
                    f"{self.base_url}/text/chatcompletion_v2",
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                    stream=stream,
                )
                response.raise_for_status()
                return response.json() if not stream else response
                
            except requests.exceptions.RequestException as e:
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    continue
                raise RuntimeError(f"MiniMax API call failed after {self.max_retries} attempts: {e}")
    
    def chat(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> tuple[str, int, int, float]:
        """Send a chat request and get complete response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            
        Returns:
            Tuple of (response_text, input_tokens, output_tokens, cost_usd)
        """
        # Estimate input tokens
        input_text = "\n".join(m.get("content", "") for m in messages)
        input_tokens = self._estimate_tokens(input_text)
        
        # Call API
        response = self._call_api(messages, temperature, max_tokens, stream=False)
        
        # Extract response
        if "choices" in response and len(response["choices"]) > 0:
            content = response["choices"][0]["message"]["content"]
        else:
            content = ""
        
        # Get actual token counts if available
        output_tokens = response.get("usage", {}).get("completion_tokens", self._estimate_tokens(content))
        input_tokens = response.get("usage", {}).get("prompt_tokens", input_tokens)
        
        # Calculate cost
        cost = (input_tokens / 1_000_000 * TOKEN_COST_INPUT + 
                output_tokens / 1_000_000 * TOKEN_COST_OUTPUT)
        
        return content, input_tokens, output_tokens, cost
    
    def chat_stream(
        self,
        messages: list[dict],
        temperature: float = 0.7,
        max_tokens: int = 4000,
    ) -> Generator[tuple[str, int, int, float], None, None]:
        """Send a chat request with streaming response.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Max tokens in response
            
        Yields:
            Tuple of (chunk_text, cumulative_input_tokens, cumulative_output_tokens, cost_usd)
        """
        # Estimate input tokens
        input_text = "\n".join(m.get("content", "") for m in messages)
        input_tokens = self._estimate_tokens(input_text)
        
        # Call API with streaming
        response = self._call_api(messages, temperature, max_tokens, stream=True)
        
        accumulated_text = ""
        output_tokens = 0
        
        for line in response.iter_lines():
            if line:
                line = line.decode("utf-8")
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        if "choices" in chunk and len(chunk["choices"]) > 0:
                            delta = chunk["choices"][0].get("delta", {})
                            if "content" in delta:
                                chunk_text = delta["content"]
                                accumulated_text += chunk_text
                                output_tokens = self._estimate_tokens(accumulated_text)
                                cost = (input_tokens / 1_000_000 * TOKEN_COST_INPUT + 
                                        output_tokens / 1_000_000 * TOKEN_COST_OUTPUT)
                                yield chunk_text, input_tokens, output_tokens, cost
                    except json.JSONDecodeError:
                        continue
        
        # Final yield with complete text
        cost = (input_tokens / 1_000_000 * TOKEN_COST_INPUT + 
                output_tokens / 1_000_000 * TOKEN_COST_OUTPUT)
        yield "", input_tokens, output_tokens, cost
    
    def validate_connection(self) -> bool:
        """Validate API connection.
        
        Returns:
            True if connection is valid
        """
        try:
            result, _, _, _ = self.chat(
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
            )
            return len(result) > 0
        except Exception:
            return False
