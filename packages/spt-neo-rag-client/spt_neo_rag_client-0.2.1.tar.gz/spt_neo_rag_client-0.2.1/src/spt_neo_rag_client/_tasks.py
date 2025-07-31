"""Task endpoints for the SPT Neo RAG Client."""

import asyncio
from typing import Callable, Coroutine, Dict, Any, Optional, List
from uuid import UUID

from .models import (
    TaskResponse,
)

# Type alias for the request function
RequestFunc = Callable[..., Coroutine[Any, Any, Any]]


class TaskEndpoints:
    """Handles task-related API operations."""

    def __init__(self, request_func: RequestFunc):
        self._request = request_func

    async def list_tasks(self) -> List[TaskResponse]:
        """
        Get all tasks.
        
        Returns:
            List[TaskResponse]: List of all tasks.
        """
        response = await self._request("GET", "/tasks")
        return [TaskResponse(**item) for item in response.json()]

    def list_tasks_sync(self) -> List[TaskResponse]:
        """Synchronous version of list_tasks."""
        return asyncio.run(self.list_tasks())

    async def get_task(self, task_id: UUID) -> TaskResponse:
        """
        Get details for a specific task.

        Args:
            task_id: ID of the task.
            
        Returns:
            TaskResponse: Task details.
        """
        response = await self._request("GET", f"/tasks/{task_id}")
        return TaskResponse(**response.json())

    def get_task_sync(self, task_id: UUID) -> TaskResponse:
        """Synchronous version of get_task."""
        return asyncio.run(self.get_task(task_id))

    async def delete_task(self, task_id: UUID) -> Dict[str, Any]:
        """
        Cancel a running task (sends delete request).

        Args:
            task_id: ID of the task to cancel.
            
        Returns:
            Dict[str, Any]: Confirmation message (or None on 204).
        """
        response = await self._request("DELETE", f"/tasks/{task_id}")
        # Returns 204 No Content on success
        if response.status_code == 204:
            return {"status": "success", "message": f"Task {task_id} cancellation requested."}
        return response.json() # Should ideally not happen on success

    def delete_task_sync(self, task_id: UUID) -> Dict[str, Any]:
        """Synchronous version of delete_task."""
        return asyncio.run(self.delete_task(task_id))

    async def get_document_tasks(self, document_id: UUID) -> List[TaskResponse]:
        """
        Get all tasks related to a specific document.

        Args:
            document_id: ID of the document.
            
        Returns:
            List[TaskResponse]: List of tasks for the document.
        """
        response = await self._request("GET", f"/tasks/document/{document_id}")
        return [TaskResponse(**item) for item in response.json()]

    def get_document_tasks_sync(self, document_id: UUID) -> List[TaskResponse]:
        """Synchronous version of get_document_tasks."""
        return asyncio.run(self.get_document_tasks(document_id)) 