"""Query endpoints for the SPT Neo RAG Client."""

import asyncio
import json
from typing import Callable, Coroutine, Dict, Any, Optional, List, AsyncGenerator
from uuid import UUID

import httpx

from .models import (
    QueryResponse,
    QueryStrategyResponse,
)
from .exceptions import NeoRagApiError

# Type alias for the request function
RequestFunc = Callable[..., Coroutine[Any, Any, httpx.Response]]


class QueryEndpoints:
    """Handles query-related API operations."""

    def __init__(self, request_func: RequestFunc):
        self._request = request_func

    async def query(
        self,
        query: str,
        knowledge_base_ids: List[UUID],
        query_strategy: str = "default",
        llm_config: Optional[Dict[str, Any]] = None,
        num_results: int = 5,
        credentials: Optional[List[str]] = None,
        use_cag: bool = False, # Cache-Augmented Generation
        include_sources: bool = True,
    ) -> QueryResponse:
        """
        Execute a query against one or more knowledge bases.

        Args:
            query: The search query string.
            knowledge_base_ids: List of knowledge base IDs to query against.
            query_strategy: Query strategy to use (default: "default").
            llm_config: Optional LLM configuration overrides.
            num_results: Number of relevant sources to retrieve.
            credentials: User credentials for access control.
            use_cag: Use Cache-Augmented Generation (uses full docs).
            include_sources: Whether to include source documents in the response.
            
        Returns:
            QueryResponse: The query results.
        """
        query_data = {
            "query": query,
            "knowledge_base_ids": [str(kb_id) for kb_id in knowledge_base_ids],
            "query_strategy": query_strategy,
            "llm_config": llm_config or {},
            "num_results": num_results,
            "credentials": credentials or ["ALL"],
            "use_cag": use_cag,
            "include_sources": include_sources,
            "stream": False,
        }
        response = await self._request("POST", "/queries", json_data=query_data)
        return QueryResponse(**response.json())

    def query_sync(
        self,
        query: str,
        knowledge_base_ids: List[UUID],
        query_strategy: str = "default",
        llm_config: Optional[Dict[str, Any]] = None,
        num_results: int = 5,
        credentials: Optional[List[str]] = None,
        use_cag: bool = False,
        include_sources: bool = True,
    ) -> QueryResponse:
        """Synchronous version of query."""
        return asyncio.run(self.query(
            query=query, knowledge_base_ids=knowledge_base_ids,
            query_strategy=query_strategy, llm_config=llm_config,
            num_results=num_results, credentials=credentials,
            use_cag=use_cag, include_sources=include_sources
        ))

    async def stream_query(
        self,
        query: str,
        knowledge_base_ids: List[UUID],
        query_strategy: str = "default",
        llm_config: Optional[Dict[str, Any]] = None,
        num_results: int = 5,
        credentials: Optional[List[str]] = None,
        use_cag: bool = False, # Cache-Augmented Generation
        include_sources: bool = True,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream a query response from one or more knowledge bases.

        Yields chunks of the response as JSON objects.
        Final chunk includes sources if requested and `done=True`.

        Args:
            query: The search query string.
            knowledge_base_ids: List of knowledge base IDs to query against.
            query_strategy: Query strategy to use (default: "default").
            llm_config: Optional LLM configuration overrides.
            num_results: Number of relevant sources to retrieve.
            credentials: User credentials for access control.
            use_cag: Use Cache-Augmented Generation (uses full docs).
            include_sources: Whether to include source documents in the final chunk.
            
        Yields:
            Dict[str, Any]: Chunks of the streaming response.
        """
        query_data = {
            "query": query,
            "knowledge_base_ids": [str(kb_id) for kb_id in knowledge_base_ids],
            "query_strategy": query_strategy,
            "llm_config": llm_config or {},
            "num_results": num_results,
            "credentials": credentials or ["ALL"],
            "use_cag": use_cag,
            "include_sources": include_sources,
            "stream": True,
        }
        
        # Use httpx's stream capabilities directly for NDJSON
        # Need to bypass the standard _request method for streaming
        # Assuming self._request was injected from NeoRagClient which has access
        # to base URL and auth.
        # This part needs careful handling in the main client refactor.
        # Let's assume NeoRagClient provides a way to get the AsyncClient instance.
        
        # Placeholder: This stream handling needs refinement based on NeoRagClient access
        async with httpx.AsyncClient(timeout=self._request.__self__.timeout) as client:
            url = f"{self._request.__self__.api_v1_url}/queries/stream"
            headers = self._request.__self__.auth.get_headers()
            try:
                async with client.stream("POST", url, json=query_data, headers=headers) as response:
                    if response.status_code >= 400:
                        error_detail = await response.aread()
                        raise NeoRagApiError(
                            status_code=response.status_code,
                            detail=json.loads(error_detail) if error_detail else f"HTTP Error {response.status_code}",
                            headers=dict(response.headers),
                        )
                        
                    async for line in response.aiter_lines():
                        if line:
                            try:
                                yield json.loads(line)
                            except json.JSONDecodeError:
                                print(f"Warning: Could not decode stream line: {line}") # Log warning
                                continue
            except httpx.RequestError as e:
                 raise httpx.NetworkError(f"Stream request failed: {str(e)}", original_error=e)

    def stream_query_sync(
        self,
        query: str,
        knowledge_base_ids: List[UUID],
        query_strategy: str = "default",
        llm_config: Optional[Dict[str, Any]] = None,
        num_results: int = 5,
        credentials: Optional[List[str]] = None,
        use_cag: bool = False,
        include_sources: bool = True,
    ) -> List[Dict[str, Any]]:
        """Synchronous version of stream_query. Collects all chunks."""
        async def collect_chunks():
            chunks = []
            async for chunk in self.stream_query(
                query=query, knowledge_base_ids=knowledge_base_ids,
                query_strategy=query_strategy, llm_config=llm_config,
                num_results=num_results, credentials=credentials,
                use_cag=use_cag, include_sources=include_sources
            ):
                chunks.append(chunk)
            return chunks
        return asyncio.run(collect_chunks())

    async def get_query_strategies(self) -> QueryStrategyResponse:
        """
        Get available query strategies.
        
        Returns:
            QueryStrategyResponse: List of available strategies.
        """
        response = await self._request("GET", "/queries/strategies")
        return QueryStrategyResponse(**response.json())

    def get_query_strategies_sync(self) -> QueryStrategyResponse:
        """Synchronous version of get_query_strategies."""
        return asyncio.run(self.get_query_strategies()) 