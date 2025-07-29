"""
Monkey Coder Python SDK client implementation

This module provides a robust client implementation for interacting with the
Monkey Coder API. It handles authentication, retries, streaming, and more.
"""

import requests
from requests.adapters import HTTPAdapter, Retry
import json
from typing import Dict, Callable, Optional
from .types import (
    ExecuteRequest,
    ExecuteResponse,
    HealthResponse,
    StreamEvent,
    UsageRequest,
    ProviderType,
    MonkeyCoderClientConfig,
    MonkeyCoderError,
    MonkeyCoderAPIError,
    MonkeyCoderNetworkError,
    MonkeyCoderStreamError
)


class MonkeyCoderClient:
    """
    Monkey Coder SDK client for the Python language.

    Provides a comprehensive interface to work with Monkey Coder API for 
    task management, health checks, and usage analysis.
    """

    def __init__(self, config: Optional[MonkeyCoderClientConfig] = None):
        config = config or MonkeyCoderClientConfig()
        self.base_url = config.base_url.rstrip('/')
        self.api_key = config.api_key
        self.timeout = config.timeout

        # Setup request session with retries
        self.session = requests.Session()
        retries = Retry(
            total=config.retries,
            backoff_factor=config.retry_delay,
            status_forcelist=[502, 503, 504],
            method_whitelist=["HEAD", "GET", "OPTIONS", "POST"]
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        # Custom retry condition
        self.retry_condition = config.retry_condition or self.default_retry_condition

    def default_retry_condition(self, exception: Exception) -> bool:
        """Default condition for request retries."""
        return isinstance(exception, (MonkeyCoderNetworkError,))

    def make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """
        Make an HTTP request to the Monkey Coder API.

        Args:
            method: HTTP method
            endpoint: API endpoint
            **kwargs: Additional request parameters

        Returns:
            Parsed JSON response

        Raises:
            MonkeyCoderError: For general API errors
            MonkeyCoderAPIError: For specific API errors
            MonkeyCoderNetworkError: For network-related errors
        """
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f'Bearer {self.api_key}'
        headers['Content-Type'] = 'application/json'
        try:
            response = self.session.request(
                method,
                url,
                headers=headers,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            raise MonkeyCoderAPIError(
                f"HTTP error occurred: {http_err}",
                code=str(http_err.response.status_code)
            )
        except requests.exceptions.RequestException as err:
            raise MonkeyCoderNetworkError(f"Request error: {err}")

    def health(self) -> HealthResponse:
        """
        Perform a health check on the Monkey Coder API.

        Returns:
            HealthResponse object
        """
        data = self.make_request('GET', '/health')
        return HealthResponse(**data)

    def execute(self, request: ExecuteRequest) -> ExecuteResponse:
        """
        Execute a task using the Monkey Coder API.

        Args:
            request: ExecuteRequest object

        Returns:
            ExecuteResponse object
        """
        data = self.make_request(
            'POST',
            '/v1/execute',
            json=request.__dict__,
        )
        return ExecuteResponse(**data)

    def execute_stream(self, request: ExecuteRequest, on_event: Callable[[StreamEvent], None]) -> None:
        """
        Execute a task with streaming support using the Monkey Coder API.

        Args:
            request: ExecuteRequest object
            on_event: Callback function for handling stream events

        Raises:
            MonkeyCoderStreamError: For streaming errors
        """
        url = f"{self.base_url}/v1/execute/stream"
        headers = {'Authorization': f'Bearer {self.api_key}', 'Accept': 'text/event-stream'}

        try:
            response = self.session.post(url, headers=headers, json=request.__dict__, stream=True)
            response.raise_for_status()

            for line in response.iter_lines(decode_unicode=True):
                if line.startswith('data: '):
                    try:
                        data = json.loads(line[6:])
                        event = StreamEvent(**data)
                        on_event(event)
                        if event.type == 'error':
                            raise MonkeyCoderStreamError(event.error.message, event.error.code)
                    except json.JSONDecodeError as json_err:
                        raise MonkeyCoderStreamError(f"Failed to decode stream event: {json_err}")
        except requests.exceptions.RequestException as err:
            raise MonkeyCoderStreamError(f"Streaming request error: {err}")

    def get_usage(self, usage_request: UsageRequest) -> Dict:
        """
        Retrieve usage metrics for the Monkey Coder API.

        Args:
            usage_request: Usage request parameters

        Returns:
            Dictionary with usage statistics
        """
        return self.make_request('GET', '/v1/billing/usage', params=usage_request.__dict__)
    
    def list_providers(self) -> Dict:
        """
        List available AI providers and their status.

        Returns:
            Dictionary with provider information
        """
        return self.make_request('GET', '/v1/providers')

    def list_models(self, provider: Optional[ProviderType] = None) -> Dict:
        """
        List available AI models by provider.

        Args:
            provider: Optional provider filter

        Returns:
            Dictionary with model information
        """
        params = {'provider': provider} if provider else None
        return self.make_request('GET', '/v1/models', params=params)
    
    def debug_routing(self, request: ExecuteRequest) -> Dict:
        """
        Debug routing decisions for a given request.

        Args:
            request: ExecuteRequest object

        Returns:
            Detailed debug information
        """
        return self.make_request('POST', '/v1/router/debug', json=request.__dict__)
