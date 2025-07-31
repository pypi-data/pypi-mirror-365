"""Structured Schema endpoints for the SPT Neo RAG Client."""

import asyncio
from typing import Callable, Coroutine, Dict, Any, Optional, List
from uuid import UUID

from .models import (
    StructuredSchemaCreateRequest,
    StructuredSchemaUpdateRequest,
    StructuredSchemaResponse,
    GenericStatusResponse,
)

# Type alias for the request function
RequestFunc = Callable[..., Coroutine[Any, Any, Any]]


class StructuredSchemaEndpoints:
    """Handles structured schema-related API operations."""

    def __init__(self, request_func: RequestFunc):
        self._request = request_func

    async def create_schema(
        self, create_data: StructuredSchemaCreateRequest
    ) -> StructuredSchemaResponse:
        """
        Create a new structured document schema.

        Args:
            create_data: StructuredSchemaCreateRequest with schema details.
            
        Returns:
            StructuredSchemaResponse: Created schema details.
        """
        response = await self._request(
            "POST", "/structured-schemas", json_data=create_data.model_dump()
        )
        return StructuredSchemaResponse(**response.json())

    def create_schema_sync(
        self, create_data: StructuredSchemaCreateRequest
    ) -> StructuredSchemaResponse:
        """Synchronous version of create_schema."""
        return asyncio.run(self.create_schema(create_data))

    async def list_schemas(
        self, skip: int = 0, limit: int = 100
    ) -> List[StructuredSchemaResponse]:
        """
        List all structured document schemas.

        Args:
            skip: Number of schemas to skip.
            limit: Maximum number of schemas to return.
            
        Returns:
            List[StructuredSchemaResponse]: List of schemas.
        """
        params = {"skip": skip, "limit": limit}
        response = await self._request("GET", "/structured-schemas", params=params)
        return [StructuredSchemaResponse(**item) for item in response.json()]

    def list_schemas_sync(
        self, skip: int = 0, limit: int = 100
    ) -> List[StructuredSchemaResponse]:
        """Synchronous version of list_schemas."""
        return asyncio.run(self.list_schemas(skip, limit))

    async def get_schema(self, schema_id: UUID) -> StructuredSchemaResponse:
        """
        Get a specific structured document schema by ID.

        Args:
            schema_id: ID of the schema.
            
        Returns:
            StructuredSchemaResponse: Schema details.
        """
        response = await self._request("GET", f"/structured-schemas/{schema_id}")
        return StructuredSchemaResponse(**response.json())

    def get_schema_sync(self, schema_id: UUID) -> StructuredSchemaResponse:
        """Synchronous version of get_schema."""
        return asyncio.run(self.get_schema(schema_id))

    async def update_schema(
        self, schema_id: UUID, update_data: StructuredSchemaUpdateRequest
    ) -> StructuredSchemaResponse:
        """
        Update an existing structured document schema.

        Args:
            schema_id: ID of the schema to update.
            update_data: StructuredSchemaUpdateRequest with fields to change.
            
        Returns:
            StructuredSchemaResponse: Updated schema details.
        """
        response = await self._request(
            "PUT",
            f"/structured-schemas/{schema_id}",
            json_data=update_data.model_dump(exclude_unset=True),
        )
        return StructuredSchemaResponse(**response.json())

    def update_schema_sync(
        self, schema_id: UUID, update_data: StructuredSchemaUpdateRequest
    ) -> StructuredSchemaResponse:
        """Synchronous version of update_schema."""
        return asyncio.run(self.update_schema(schema_id, update_data))

    async def delete_schema(self, schema_id: UUID) -> Dict[str, Any]:
        """
        Delete a structured document schema.

        Args:
            schema_id: ID of the schema to delete.
            
        Returns:
            Dict[str, Any]: Confirmation message (or None on 204).
        """
        response = await self._request("DELETE", f"/structured-schemas/{schema_id}")
        # Returns 204 No Content on success
        if response.status_code == 204:
            return {"status": "success", "message": f"Schema {schema_id} deleted."}
        return response.json() # Should ideally not happen on success

    def delete_schema_sync(self, schema_id: UUID) -> Dict[str, Any]:
        """Synchronous version of delete_schema."""
        return asyncio.run(self.delete_schema(schema_id)) 