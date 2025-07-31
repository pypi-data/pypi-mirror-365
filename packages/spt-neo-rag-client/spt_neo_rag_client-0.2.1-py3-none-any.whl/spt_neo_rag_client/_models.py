"""Model endpoints for the SPT Neo RAG Client."""

import asyncio
from typing import Dict, Any, Optional, List, TYPE_CHECKING

from .models import ModelInfo

if TYPE_CHECKING:
    from .client import NeoRagClient


class ModelEndpoints:
    """Handles model-related API operations."""

    def __init__(self, client: "NeoRagClient"):
        self._client = client

    async def get_models(
        self, provider: str, model_type: Optional[str] = None
    ) -> List[ModelInfo]:
        """
        Get available models for a specific provider.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic').
            model_type: Optional model type filter (e.g., 'embedding', 'chat').
            
        Returns:
            List[ModelInfo]: List of available models.
        """
        params = {"provider": provider}
        if model_type:
            params["type"] = model_type
            
        response = await self._client._request("GET", "/models/list", params=params)
        return [ModelInfo(**item) for item in response.json()]

    def get_models_sync(
        self, provider: str, model_type: Optional[str] = None
    ) -> List[ModelInfo]:
        """Synchronous version of get_models."""
        return asyncio.run(self.get_models(provider, model_type))

    async def get_model_names(
        self, provider: str, model_type: Optional[str] = None
    ) -> List[str]:
        """
        Get available model names for a specific provider.

        Args:
            provider: Provider name (e.g., 'openai', 'anthropic').
            model_type: Optional model type filter (e.g., 'embedding', 'chat').
            
        Returns:
            List[str]: List of available model names.
        """
        params = {"provider": provider}
        if model_type:
            params["type"] = model_type
            
        response = await self._client._request("GET", "/models/names", params=params)
        return response.json()

    def get_model_names_sync(
        self, provider: str, model_type: Optional[str] = None
    ) -> List[str]:
        """Synchronous version of get_model_names."""
        return asyncio.run(self.get_model_names(provider, model_type))

    async def get_providers(self) -> List[str]:
        """
        Get available providers.
        
        Returns:
            List[str]: List of available providers.
        """
        response = await self._client._request("GET", "/models/providers")
        return response.json()

    def get_providers_sync(self) -> List[str]:
        """Synchronous version of get_providers."""
        return asyncio.run(self.get_providers()) 