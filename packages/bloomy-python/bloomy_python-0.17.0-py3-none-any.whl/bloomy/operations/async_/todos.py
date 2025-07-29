"""Async todo operations for the Bloomy SDK."""

from __future__ import annotations

import builtins
from datetime import datetime
from typing import TYPE_CHECKING

from ...models import Todo
from ...utils.async_base_operations import AsyncBaseOperations

if TYPE_CHECKING:
    from typing import Any

    import httpx


class AsyncTodoOperations(AsyncBaseOperations):
    """Async class to handle all operations related to todos.

    Note:
        This class is already initialized via the client and usable as
        `client.todo.method`

    """

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Initialize the async todo operations.

        Args:
            client: The async HTTP client to use for API requests.

        """
        super().__init__(client)

    async def list(
        self, user_id: int | None = None, meeting_id: int | None = None
    ) -> builtins.list[Todo]:
        """List all todos for a specific user or meeting.

        Args:
            user_id: The ID of the user (default is the initialized user ID)
            meeting_id: The ID of the meeting

        Returns:
            A list of Todo model instances

        Raises:
            ValueError: If both user_id and meeting_id are provided

        Example:
            ```python
            # Fetch todos for the current user
            await client.todo.list()
            # Returns: [Todo(id=1, name='New Todo', due_date='2024-06-15', ...)]
            ```

        """
        if user_id is not None and meeting_id is not None:
            raise ValueError(
                "Please provide either `user_id` or `meeting_id`, not both."
            )

        if meeting_id is not None:
            response = await self._client.get(f"L10/{meeting_id}/todos")
        else:
            if user_id is None:
                user_id = await self.get_user_id()
            response = await self._client.get(f"todo/user/{user_id}")

        response.raise_for_status()
        data = response.json()

        return [Todo.model_validate(todo) for todo in data]

    async def create(
        self,
        title: str,
        meeting_id: int | None = None,
        due_date: str | None = None,
        user_id: int | None = None,
        notes: str | None = None,
    ) -> Todo:
        """Create a new todo.

        Args:
            title: The title of the new todo
            meeting_id: The ID of the meeting associated with the todo (optional)
            due_date: The due date of the todo (optional)
            user_id: The ID of the user responsible for the todo
                (default: initialized user ID)
            notes: Additional notes for the todo (optional)

        Returns:
            A Todo model instance representing the newly created todo

        Example:
            ```python
            # Create a user todo
            await client.todo.create(
                title="New Todo", due_date="2024-06-15"
            )

            # Create a meeting todo
            await client.todo.create(
                title="Meeting Action", meeting_id=1, due_date="2024-06-15"
            )
            ```

        """
        if user_id is None:
            user_id = await self.get_user_id()

        payload: dict[str, Any] = {
            "title": title,
            "accountableUserId": user_id,
        }

        if notes is not None:
            payload["notes"] = notes

        if due_date is not None:
            payload["dueDate"] = due_date

        if meeting_id is not None:
            # Meeting todo
            payload["meetingid"] = meeting_id
            response = await self._client.post("todo/createmeetingtodo", json=payload)
        else:
            # User todo
            response = await self._client.post("todo/create", json=payload)

        response.raise_for_status()
        data = response.json()

        # Add default values for fields that might be missing in create response
        todo_data = {
            "Id": data["Id"],
            "Name": data["Name"],
            "DetailsUrl": data.get("DetailsUrl"),
            "DueDate": data.get("DueDate"),
            "CompleteTime": None,
            "CreateTime": data.get("CreateTime", datetime.now().isoformat()),
            "OriginId": meeting_id,
            "Origin": None,
            "Complete": False,
        }

        return Todo.model_validate(todo_data)

    async def complete(self, todo_id: int) -> bool:
        """Mark a todo as complete.

        Args:
            todo_id: The ID of the todo to complete

        Returns:
            True if the operation was successful

        Example:
            ```python
            await client.todo.complete(1)
            # Returns: True
            ```

        """
        response = await self._client.post(f"todo/{todo_id}/complete?status=true")
        response.raise_for_status()
        return response.is_success

    async def update(
        self,
        todo_id: int,
        title: str | None = None,
        due_date: str | None = None,
    ) -> Todo:
        """Update an existing todo.

        Args:
            todo_id: The ID of the todo to update
            title: The new title of the todo (optional)
            due_date: The new due date of the todo (optional)

        Returns:
            A Todo model instance containing the updated todo details

        Raises:
            ValueError: If no update fields are provided
            RuntimeError: If the update request fails

        Example:
            ```python
            await client.todo.update(
                todo_id=1, title="Updated Todo", due_date="2024-11-01"
            )
            # Returns: Todo(id=1, name='Updated Todo', due_date='2024-11-01', ...)
            ```

        """
        payload: dict[str, Any] = {}

        if title is not None:
            payload["title"] = title

        if due_date is not None:
            payload["dueDate"] = due_date

        if not payload:
            raise ValueError("At least one field must be provided")

        response = await self._client.put(f"todo/{todo_id}", json=payload)

        if response.status_code != 200:
            raise RuntimeError(f"Failed to update todo. Status: {response.status_code}")

        # Construct todo data for validation
        todo_data = {
            "Id": todo_id,
            "Name": title or "",
            "DetailsUrl": "",
            "DueDate": due_date,
            "CompleteTime": None,
            "CreateTime": datetime.now().isoformat(),
            "OriginId": None,
            "Origin": None,
            "Complete": False,
        }

        return Todo.model_validate(todo_data)

    async def details(self, todo_id: int) -> Todo:
        """Retrieve the details of a specific todo item by its ID.

        Args:
            todo_id: The ID of the todo item to retrieve

        Returns:
            A Todo model instance containing the todo details

        Raises:
            RuntimeError: If the request to retrieve the todo details fails

        Example:
            ```python
            await client.todo.details(1)
            # Returns: Todo(id=1, name='Updated Todo', due_date='2024-11-01', ...)
            ```

        """
        response = await self._client.get(f"todo/{todo_id}")

        if not response.is_success:
            raise RuntimeError(
                f"Failed to get todo details. Status: {response.status_code}"
            )

        response.raise_for_status()
        todo = response.json()

        return Todo.model_validate(todo)
