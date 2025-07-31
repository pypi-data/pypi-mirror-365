"""
SPT Neo RAG Client implementation.

This module contains the main client class for interacting with the SPT Neo RAG API.
"""

import json
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator, BinaryIO, Union
from uuid import UUID

import httpx
from pydantic import TypeAdapter

from .auth import Auth
from .exceptions import NeoRagApiError, ConfigurationError, NetworkError
from .models import (
    Token,
    UserCreate,
    UserResponse,
    ApiKeyCreate,
    ApiKeyResponse,
    ApiKeyFullResponse,
    KnowledgeBaseCreate,
    KnowledgeBaseUpdate,
    KnowledgeBaseConfigUpdate,
    KnowledgeBaseResponse,
    DocumentUpdate,
    DocumentResponse,
    DocumentChunkResponse,
    DocumentPageImageResponse,
    QueryResponse,
    TaskResponse,
    PasswordResetRequest,
    GenericStatusResponse,
)

# Import endpoint classes
from ._admin import AdminEndpoints
from ._api_keys import ApiKeyEndpoints
from ._bm25 import BM25Endpoints
from ._content import ContentEndpoints
from ._documents import DocumentEndpoints
from ._health import HealthEndpoints
from ._knowledge_bases import KnowledgeBaseEndpoints
from ._knowledge_graph import KnowledgeGraphEndpoints
from ._models import ModelEndpoints
from ._queries import QueryEndpoints
from ._structured_schemas import StructuredSchemaEndpoints
from ._tasks import TaskEndpoints
from ._teams import TeamEndpoints
from ._users import UserEndpoints
from ._webhooks import WebhookEndpoints


class NeoRagClient:
    """
    Client for the SPT Neo RAG API.
    
    Provides access to various API endpoints through dedicated attributes:
    - admin: Admin operations
    - api_keys: API key management
    - bm25: BM25 index operations
    - content: Content storage operations
    - documents: Document management
    - health: Health checks
    - knowledge_bases: Knowledge base management
    - knowledge_graph: Knowledge graph operations
    - models: Model information
    - queries: Query execution
    - structured_schemas: Structured schema management
    - tasks: Background task management
    - teams: Team management
    - users: User management (requires admin usually)
    - webhooks: Webhook configuration
    """
    
    def __init__(
        self,
        base_url: str,
        api_key: Optional[str] = None,
        timeout: Optional[float] = 60.0,
    ):
        """
        Initialize the SPT Neo RAG client.
        
        Args:
            base_url: Base URL of the API (e.g., https://api.example.com)
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_v1_url = f"{self.base_url}/api/v1"
        self.timeout = timeout
        self._auth = Auth(base_url=self.base_url, api_key=api_key)
        
        # Instantiate endpoint handlers, passing the client instance
        self.admin = AdminEndpoints(self) 
        self.api_keys = ApiKeyEndpoints(self)
        self.bm25 = BM25Endpoints(self)
        self.content = ContentEndpoints(self)
        self.documents = DocumentEndpoints(self)
        self.health = HealthEndpoints(self)
        self.knowledge_bases = KnowledgeBaseEndpoints(self)
        self.knowledge_graph = KnowledgeGraphEndpoints(self)
        self.models = ModelEndpoints(self)
        self.queries = QueryEndpoints(self)
        self.structured_schemas = StructuredSchemaEndpoints(self)
        self.tasks = TaskEndpoints(self)
        self.teams = TeamEndpoints(self)
        self.users = UserEndpoints(self)
        self.webhooks = WebhookEndpoints(self)
        
    async def __aenter__(self):
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
        
    async def close(self):
        """Close the client and release resources."""
        await self._auth.close()
        
    def _check_auth(self):
        """Check if the client is authenticated."""
        if not self._auth.is_authenticated:
            raise ConfigurationError(
                "Client is not authenticated. Please provide an API key or call login()."
            )
            
    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        files: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
        is_stream_request: bool = False, # Flag for streaming
    ) -> httpx.Response:
        """
        Make an HTTP request to the API.
        Handles authentication and error responses.
        """
        self._check_auth()
        
        url = f"{self.api_v1_url}/{path.lstrip('/')}"
        request_headers = self._auth.get_headers()
        
        if headers:
            request_headers.update(headers)
            
        # NOTE: Stream handling is now managed within the QueryEndpoints.stream_query
        # The main _request handles non-streaming requests.
        if is_stream_request:
             raise NotImplementedError("Streaming should be handled by specific endpoint methods.")

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json_data,
                    data=data,
                    files=files,
                    headers=request_headers,
                )
                
                response.raise_for_status()
                return response
                
        except httpx.HTTPStatusError as e:
            try:
                # Attempt to parse JSON error detail
                 error_detail = e.response.json()
            except json.JSONDecodeError:
                 # Fallback to raw text if not JSON
                 error_detail = e.response.text if e.response.text else str(e)
                 
            raise NeoRagApiError(
                status_code=e.response.status_code,
                detail=error_detail,
                headers=dict(e.response.headers),
            )
            
        except httpx.RequestError as e:
            raise NetworkError(f"Request failed: {str(e)}", original_error=e)
    
    # --- Core Authentication / User Methods --- 
    
    async def login(self, username: str, password: str) -> Token:
        """
        Authenticate with username and password.
        
        Args:
            username: User's email
            password: User's password
            
        Returns:
            Token: Authentication token
        """
        return await self._auth.login(username, password)

    def login_sync(self, username: str, password: str) -> Token:
        """Synchronous version of login."""
        return asyncio.run(self.login(username, password))
    
    async def logout(self) -> bool:
        """
        Logout the current user.
        
        Returns:
            bool: True if logout was successful (or endpoint returns success)
        """
        # Logout in auth module handles token clearing
        # Optionally call the backend endpoint if needed for server-side logging
        try:
            await self._request("POST", "/auth/logout")
            await self._auth.logout() # Clear local token state
            return True
        except Exception:
            # Attempt local logout even if backend call fails
            await self._auth.logout()
            return False 

    def logout_sync(self) -> bool:
        """Synchronous version of logout."""
        return asyncio.run(self.logout())
    
    def set_api_key(self, api_key: str):
        """
        Set the API key for subsequent requests.
        
        Args:
            api_key: API key
        """
        self._auth.set_api_key(api_key)
        
    async def get_current_user(self) -> UserResponse:
        """
        Get information about the currently authenticated user.
        Corresponds to `/auth/me`.
        
        Returns:
            UserResponse: Current user details.
        """
        response = await self._request("GET", "/auth/me")
        return UserResponse(**response.json())

    def get_current_user_sync(self) -> UserResponse:
        """Synchronous version of get_current_user."""
        return asyncio.run(self.get_current_user())

    async def register(self, email: str, password: str, name: str) -> UserResponse:
        """
        Register a new user.
        
        Args:
            email: User's email
            password: User's password
            name: User's name
            
        Returns:
            UserResponse: Created user
        """
        user_dict = await self._auth.register(email, password, name)
        return UserResponse(**user_dict)

    def register_sync(self, email: str, password: str, name: str) -> UserResponse:
        """Synchronous version of register."""
        return asyncio.run(self.register(email, password, name))

    async def change_password(self, current_password: str, new_password: str) -> bool:
        """
        Change the password for the current user.

        Args:
            current_password: The user's current password.
            new_password: The desired new password.

        Returns:
            bool: True if password change was successful
        """
        return await self._auth.change_password(current_password, new_password)

    def change_password_sync(self, current_password: str, new_password: str) -> bool:
        """Synchronous version of change_password."""
        return asyncio.run(self.change_password(current_password, new_password))

    async def request_password_reset(self, email: str) -> Dict[str, str]:
        """
        Request a password reset for the given email address.

        Args:
            email: The email address of the user.

        Returns:
            Dict[str, str]: A confirmation message.
        """
        return await self._auth.request_password_reset(email)

    def request_password_reset_sync(self, email: str) -> Dict[str, str]:
        """Synchronous version of request_password_reset."""
        return asyncio.run(self.request_password_reset(email))
    
    






    # API key management methods
    
    async def create_api_key(
        self, name: str, scopes: str = "query", expires_in_days: Optional[int] = None
    ) -> ApiKeyFullResponse:
        """
        Create a new API key.
        
        Args:
            name: Name of the API key
            scopes: Comma-separated list of scopes (query, read, write, admin)
            expires_in_days: Number of days until expiry (None for no expiry)
            
        Returns:
            ApiKeyFullResponse: Created API key with the full key
        """
        api_key_data = ApiKeyCreate(
            name=name,
            scopes=scopes,
            expires_in_days=expires_in_days,
        )
        response = await self._request(
            "POST",
            "/api-keys",
            json_data=api_key_data.model_dump(),
        )
        return ApiKeyFullResponse(**response.json())
    
    async def list_api_keys(self, skip: int = 0, limit: int = 100) -> List[ApiKeyResponse]:
        """
        List API keys for the current user.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List[ApiKeyResponse]: List of API keys
        """
        params = {"skip": skip, "limit": limit}
        response = await self._request("GET", "/api-keys", params=params)
        
        # Convert response to list of models
        adapter = TypeAdapter(List[ApiKeyResponse])
        return adapter.validate_python(response.json())
    
    async def get_api_key(self, api_key_id: Union[str, UUID]) -> ApiKeyResponse:
        """
        Get a specific API key.
        
        Args:
            api_key_id: ID of the API key
            
        Returns:
            ApiKeyResponse: API key information
        """
        response = await self._request("GET", f"/api-keys/{api_key_id}")
        return ApiKeyResponse(**response.json())
    
    async def update_api_key(
        self,
        api_key_id: Union[str, UUID],
        name: Optional[str] = None,
        scopes: Optional[str] = None,
        is_active: Optional[bool] = None,
        expires_in_days: Optional[int] = None,
    ) -> ApiKeyResponse:
        """
        Update an API key.
        
        Args:
            api_key_id: ID of the API key
            name: New name
            scopes: New scopes
            is_active: Whether the key is active
            expires_in_days: New expiry in days
            
        Returns:
            ApiKeyResponse: Updated API key
        """
        update_data = {
            "name": name,
            "scopes": scopes,
            "is_active": is_active,
            "expires_in_days": expires_in_days,
        }
        # Remove None values
        update_data = {k: v for k, v in update_data.items() if v is not None}
        
        response = await self._request(
            "PATCH",
            f"/api-keys/{api_key_id}",
            json_data=update_data,
        )
        return ApiKeyResponse(**response.json())
    
    async def delete_api_key(self, api_key_id: Union[str, UUID]) -> bool:
        """
        Delete an API key.
        
        Args:
            api_key_id: ID of the API key
            
        Returns:
            bool: True if deletion was successful
        """
        await self._request("DELETE", f"/api-keys/{api_key_id}")
        return True
    
    # Knowledge base methods
    
    async def create_knowledge_base(
        self,
        name: str,
        description: Optional[str] = None,
        kb_type: str = "default",
        config: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        credentials: Optional[List[str]] = None,
    ) -> KnowledgeBaseResponse:
        """
        Create a new knowledge base.
        
        Args:
            name: Knowledge base name
            description: Knowledge base description
            kb_type: Knowledge base type
            config: Configuration options
            metadata: Additional metadata
            credentials: Access control credentials. Default is ["ALL"] which means unrestricted access.
            
        Returns:
            KnowledgeBaseResponse: Created knowledge base
        """
        kb_data = KnowledgeBaseCreate(
            name=name,
            description=description,
            kb_type=kb_type,
            config=config,
            metadata=metadata,
            credentials=credentials,
        )
        response = await self._request(
            "POST",
            "/knowledge-bases",
            json_data=kb_data.model_dump(exclude_none=True),
        )
        return KnowledgeBaseResponse(**response.json())
    
    async def list_knowledge_bases(
        self, skip: int = 0, limit: int = 100
    ) -> List[KnowledgeBaseResponse]:
        """
        List knowledge bases.
        
        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List[KnowledgeBaseResponse]: List of knowledge bases
        """
        params = {"skip": skip, "limit": limit}
        response = await self._request("GET", "/knowledge-bases", params=params)
        
        # Convert response to list of models
        adapter = TypeAdapter(List[KnowledgeBaseResponse])
        return adapter.validate_python(response.json())
    
    async def get_knowledge_base(
        self, kb_id: Union[str, UUID]
    ) -> KnowledgeBaseResponse:
        """
        Get a specific knowledge base.
        
        Args:
            kb_id: ID of the knowledge base
            
        Returns:
            KnowledgeBaseResponse: Knowledge base information
        """
        response = await self._request("GET", f"/knowledge-bases/{kb_id}")
        return KnowledgeBaseResponse(**response.json())
    
    async def update_knowledge_base(
        self,
        kb_id: Union[str, UUID],
        name: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        credentials: Optional[List[str]] = None,
    ) -> KnowledgeBaseResponse:
        """
        Update a knowledge base.
        
        Args:
            kb_id: Knowledge base ID
            name: New name
            description: New description
            metadata: New metadata
            credentials: New access control credentials
            
        Returns:
            KnowledgeBaseResponse: Updated knowledge base
        """
        update_data = KnowledgeBaseUpdate(
            name=name,
            description=description,
            metadata=metadata,
            credentials=credentials,
        )
        # Only include non-None values
        update_data_dict = {
            k: v for k, v in update_data.model_dump().items() if v is not None
        }
        
        response = await self._request(
            "PUT",
            f"/knowledge-bases/{kb_id}",
            json_data=update_data_dict,
        )
        return KnowledgeBaseResponse(**response.json())
    
    async def update_knowledge_base_config(
        self, kb_id: Union[str, UUID], config: Dict[str, Any]
    ) -> KnowledgeBaseResponse:
        """
        Update a knowledge base's configuration.
        
        Args:
            kb_id: ID of the knowledge base
            config: New configuration
            
        Returns:
            KnowledgeBaseResponse: Updated knowledge base
        """
        config_update = KnowledgeBaseConfigUpdate(config=config)
        response = await self._request(
            "PATCH",
            f"/knowledge-bases/{kb_id}/config",
            json_data=config_update.model_dump(),
        )
        return KnowledgeBaseResponse(**response.json())
    
    async def delete_knowledge_base(self, kb_id: Union[str, UUID]) -> bool:
        """
        Delete a knowledge base.
        
        Args:
            kb_id: ID of the knowledge base
            
        Returns:
            bool: True if deletion was successful
        """
        await self._request("DELETE", f"/knowledge-bases/{kb_id}")
        return True
    
    # Document methods
    
    async def upload_document(
        self,
        file: BinaryIO,
        name: str,
        knowledge_base_id: Union[str, UUID],
        description: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        processor_type: str = "langchain",
        processor_config: Optional[Dict[str, Any]] = None,
        credentials: Optional[List[str]] = None,
        force_upload: bool = False,
    ) -> DocumentResponse:
        """
        Upload a document to a knowledge base.
        
        Args:
            file: File object to upload
            name: Document name
            knowledge_base_id: ID of the knowledge base
            description: Document description
            source: Source of the document
            metadata: Additional metadata
            processor_type: Document processor type
            processor_config: Document processor configuration
            credentials: Access control credentials for this document. If None, inherits from knowledge base.
            force_upload: Whether to force upload even if duplicate exists
            
        Returns:
            DocumentResponse: Created document
        """
        form_data = {
            "name": name,
            "knowledge_base_id": str(knowledge_base_id),
            "force_upload": "true" if force_upload else "false",
        }
        
        if description:
            form_data["description"] = description
        if source:
            form_data["source"] = source
        if processor_type:
            form_data["processor_type"] = processor_type
            
        if metadata:
            form_data["metadata"] = json.dumps(metadata)
        if processor_config:
            form_data["processor_config"] = json.dumps(processor_config)
        if credentials is not None:
            form_data["credentials"] = json.dumps(credentials)
            
        files = {"file": file}
        
        response = await self._request(
            "POST", "/documents", data=form_data, files=files
        )
        return DocumentResponse(**response.json())
    
    async def list_documents(
        self,
        knowledge_base_id: Optional[Union[str, UUID]] = None,
        skip: int = 0,
        limit: int = 100,
    ) -> List[DocumentResponse]:
        """
        List documents, optionally filtered by knowledge base.
        
        Args:
            knowledge_base_id: Optional ID of the knowledge base to filter by
            skip: Number of items to skip
            limit: Maximum number of items to return
            
        Returns:
            List[DocumentResponse]: List of documents
        """
        params = {"skip": skip, "limit": limit}
        if knowledge_base_id:
            params["knowledge_base_id"] = str(knowledge_base_id)
            
        response = await self._request("GET", "/documents/list", params=params)
        
        # Convert response to list of models
        adapter = TypeAdapter(List[DocumentResponse])
        return adapter.validate_python(response.json())
    
    async def get_document(self, document_id: Union[str, UUID]) -> DocumentResponse:
        """
        Get a specific document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            DocumentResponse: Document information
        """
        response = await self._request("GET", f"/documents/{document_id}")
        return DocumentResponse(**response.json())
    
    async def update_document(
        self,
        document_id: Union[str, UUID],
        name: Optional[str] = None,
        description: Optional[str] = None,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        credentials: Optional[List[str]] = None,
    ) -> DocumentResponse:
        """
        Update a document.
        
        Args:
            document_id: ID of the document
            name: New name
            description: New description
            source: New source
            metadata: New metadata
            credentials: New access control credentials
            
        Returns:
            DocumentResponse: Updated document
        """
        update_data = DocumentUpdate(
            name=name,
            description=description,
            source=source,
            doc_metadata=metadata,
            credentials=credentials,
        )
        # Only include non-None values
        update_data_dict = {
            k: v for k, v in update_data.model_dump().items() if v is not None
        }
        
        response = await self._request(
            "PUT",
            f"/documents/{document_id}",
            json_data=update_data_dict,
        )
        return DocumentResponse(**response.json())
    
    async def delete_document(self, document_id: Union[str, UUID]) -> bool:
        """
        Delete a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            bool: True if deletion was successful
        """
        await self._request("DELETE", f"/documents/{document_id}")
        return True
    
    async def get_document_download_url(
        self, document_id: Union[str, UUID], expiration: int = 3600
    ) -> str:
        """
        Get a pre-signed URL to download a document.
        
        Args:
            document_id: ID of the document
            expiration: URL expiration in seconds (1-24 hours)
            
        Returns:
            str: Download URL
        """
        params = {"expiration": expiration}
        response = await self._request(
            "GET", f"/documents/{document_id}/download", params=params
        )
        return response.json().get("download_url")
    
    async def get_document_chunks(
        self,
        document_id: Union[str, UUID],
        skip: int = 0,
        limit: int = 100,
        include_embeddings: bool = False,
    ) -> List[DocumentChunkResponse]:
        """
        Get chunks for a document.
        
        Args:
            document_id: ID of the document
            skip: Number of items to skip
            limit: Maximum number of items to return
            include_embeddings: Whether to include embedding vectors
            
        Returns:
            List[DocumentChunkResponse]: List of document chunks
        """
        params = {
            "skip": skip,
            "limit": limit,
            "include_embeddings": include_embeddings,
        }
        response = await self._request(
            "GET", f"/documents/{document_id}/chunks", params=params
        )
        
        # Convert response to list of models
        adapter = TypeAdapter(List[DocumentChunkResponse])
        return adapter.validate_python(response.json())
    
    async def get_document_page_images(
        self, document_id: Union[str, UUID]
    ) -> List[DocumentPageImageResponse]:
        """
        Get page images for a document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            List[DocumentPageImageResponse]: List of document page images
        """
        response = await self._request("GET", f"/documents/{document_id}/page_images")
        
        # Convert response to list of models
        adapter = TypeAdapter(List[DocumentPageImageResponse])
        return adapter.validate_python(response.json())
    
    # Query methods
    
    async def query(
        self,
        knowledge_base_id: Union[str, UUID],
        query: str,
        top_k: int = 4,
        similarity_threshold: float = 0.7,
        use_hybrid_search: bool = True,
        include_sources: bool = True,
        include_metadata: bool = False,
        query_strategy: str = "hybrid",
        query_config: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        credentials: Optional[List[str]] = ["ALL"],
    ) -> QueryResponse:
        """
        Execute a query against a knowledge base.
        
        Args:
            knowledge_base_id: ID of the knowledge base
            query: Query text
            top_k: Number of results to return
            similarity_threshold: Threshold for similarity search
            use_hybrid_search: Whether to use hybrid search
            include_sources: Whether to include sources in response
            include_metadata: Whether to include metadata in response
            query_strategy: Strategy to use for retrieval
            query_config: Additional configuration for the query
            model: LLM model to use
            provider: LLM provider to use
            credentials: User credentials for document access control
            
        Returns:
            QueryResponse: Query response
        """
        query_data = {
            "knowledge_base_id": str(knowledge_base_id),
            "query": query,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
            "use_hybrid_search": use_hybrid_search,
            "include_sources": include_sources,
            "include_metadata": include_metadata,
            "query_strategy": query_strategy,
            "stream": False,
            "credentials": credentials,
        }
        
        if query_config:
            query_data["query_config"] = query_config
        if model:
            query_data["model"] = model
        if provider:
            query_data["provider"] = provider
            
        response = await self._request("POST", "/queries", json_data=query_data)
        return QueryResponse(**response.json())
    
    async def stream_query(
        self,
        knowledge_base_id: Union[str, UUID],
        query: str,
        top_k: int = 4,
        similarity_threshold: float = 0.7,
        use_hybrid_search: bool = True,
        include_sources: bool = True,
        include_metadata: bool = False,
        query_strategy: str = "hybrid",
        query_config: Optional[Dict[str, Any]] = None,
        model: Optional[str] = None,
        provider: Optional[str] = None,
        credentials: Optional[List[str]] = ["ALL"],
    ) -> AsyncGenerator[str, None]:
        """
        Stream a query response from a knowledge base.
        
        Args:
            knowledge_base_id: ID of the knowledge base
            query: Query text
            top_k: Number of results to return
            similarity_threshold: Threshold for similarity search
            use_hybrid_search: Whether to use hybrid search
            include_sources: Whether to include sources in response
            include_metadata: Whether to include metadata in response
            query_strategy: Strategy to use for retrieval
            query_config: Additional configuration for the query
            model: LLM model to use
            provider: LLM provider to use
            credentials: User credentials for document access control
            
        Yields:
            str: Chunks of the answer as they're generated
        """
        query_data = {
            "knowledge_base_id": str(knowledge_base_id),
            "query": query,
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
            "use_hybrid_search": use_hybrid_search,
            "include_sources": include_sources,
            "include_metadata": include_metadata,
            "query_strategy": query_strategy,
            "stream": True,
            "credentials": credentials,
        }
        
        if query_config:
            query_data["query_config"] = query_config
        if model:
            query_data["model"] = model
        if provider:
            query_data["provider"] = provider
            
        self._check_auth()
        
        url = f"{self.api_v1_url}/queries/stream"
        headers = self._auth.get_headers()
        
        try:
            async with httpx.AsyncClient(timeout=None) as client:
                async with client.stream(
                    method="POST",
                    url=url,
                    json=query_data,
                    headers=headers,
                ) as response:
                    response.raise_for_status()
                    
                    async for line in response.aiter_lines():
                        if not line.strip():
                            continue
                            
                        try:
                            data = json.loads(line)
                            if data.get("chunk"):
                                yield data["chunk"]
                                
                        except json.JSONDecodeError:
                            # If not valid JSON, yield the raw line
                            yield line
                            
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json() if e.response.text else str(e)
            raise NeoRagApiError(
                status_code=e.response.status_code,
                detail=error_detail,
                headers=dict(e.response.headers),
            )
            
        except httpx.RequestError as e:
            raise NetworkError(f"Stream request failed: {str(e)}", original_error=e)
    
    # Task methods
    
    async def get_task(self, task_id: Union[str, UUID]) -> TaskResponse:
        """
        Get a specific task.
        
        Args:
            task_id: ID of the task
            
        Returns:
            TaskResponse: Task information
        """
        response = await self._request("GET", f"/tasks/{task_id}")
        return TaskResponse(**response.json())
