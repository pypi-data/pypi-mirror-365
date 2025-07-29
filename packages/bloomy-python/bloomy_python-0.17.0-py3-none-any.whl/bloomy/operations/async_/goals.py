"""Async goal operations for the Bloomy SDK."""

from __future__ import annotations

import builtins
from typing import TYPE_CHECKING

from ...models import ArchivedGoalInfo, CreatedGoalInfo, GoalInfo, GoalListResponse
from ...utils.async_base_operations import AsyncBaseOperations

if TYPE_CHECKING:
    from typing import Any

    import httpx


class AsyncGoalOperations(AsyncBaseOperations):
    """Async class to handle all operations related to goals (aka "rocks")."""

    def __init__(self, client: httpx.AsyncClient) -> None:
        """Initialize the async goal operations.

        Args:
            client: The async HTTP client to use for API requests.

        """
        super().__init__(client)

    async def list(
        self, user_id: int | None = None, archived: bool = False
    ) -> builtins.list[GoalInfo] | GoalListResponse:
        """List all goals for a specific user.

        Args:
            user_id: The ID of the user (default is the initialized user ID)
            archived: Whether to include archived goals (default: False)

        Returns:
            Either:
            - A list of GoalInfo model instances if archived is false
            - A GoalListResponse model with 'active' and 'archived' lists of
                GoalInfo instances if archived is true

        """
        if user_id is None:
            user_id = await self.get_user_id()

        response = await self._client.get(
            f"rocks/user/{user_id}", params={"include_origin": True}
        )
        response.raise_for_status()
        data = response.json()

        active_goals: list[GoalInfo] = [
            GoalInfo(
                id=goal["Id"],
                user_id=goal["Owner"]["Id"],
                user_name=goal["Owner"]["Name"],
                title=goal["Name"],
                created_at=goal["CreateTime"],
                due_date=goal["DueDate"],
                status="Completed" if goal.get("Complete") else "Incomplete",
                meeting_id=goal["Origins"][0]["Id"] if goal.get("Origins") else None,
                meeting_title=(
                    goal["Origins"][0]["Name"] if goal.get("Origins") else None
                ),
            )
            for goal in data
        ]

        if archived:
            archived_goals = await self._get_archived_goals(user_id)
            return GoalListResponse(active=active_goals, archived=archived_goals)

        return active_goals

    async def create(
        self, title: str, meeting_id: int, user_id: int | None = None
    ) -> CreatedGoalInfo:
        """Create a new goal.

        Args:
            title: The title of the new goal
            meeting_id: The ID of the meeting associated with the goal
            user_id: The ID of the user responsible for the goal (default:
                initialized user ID)

        Returns:
            A CreatedGoalInfo model instance representing the newly created goal

        """
        if user_id is None:
            user_id = await self.get_user_id()

        payload = {"title": title, "accountableUserId": user_id}
        response = await self._client.post(f"L10/{meeting_id}/rocks", json=payload)
        response.raise_for_status()
        data = response.json()

        # Map completion status
        completion_map = {2: "complete", 1: "on", 0: "off"}
        status = completion_map.get(data.get("Completion", 0), "off")

        return CreatedGoalInfo(
            id=data["Id"],
            user_id=user_id,
            user_name=data["Owner"]["Name"],
            title=title,
            meeting_id=meeting_id,
            meeting_title=data["Origins"][0]["Name"],
            status=status,
            created_at=data["CreateTime"],
        )

    async def delete(self, goal_id: int) -> bool:
        """Delete a goal.

        Args:
            goal_id: The ID of the goal to delete

        Returns:
            True if deletion was successful

        """
        response = await self._client.delete(f"rocks/{goal_id}")
        response.raise_for_status()
        return True

    async def update(
        self,
        goal_id: int,
        title: str | None = None,
        accountable_user: int | None = None,
        status: str | None = None,
    ) -> bool:
        """Update a goal.

        Args:
            goal_id: The ID of the goal to update
            title: The new title of the goal
            accountable_user: The ID of the user responsible for the goal
                (default: initialized user ID)
            status: The status value ('on', 'off', or 'complete')

        Returns:
            True if the update was successful

        Raises:
            ValueError: If an invalid status value is provided

        """
        if accountable_user is None:
            accountable_user = await self.get_user_id()

        payload: dict[str, Any] = {"accountableUserId": accountable_user}

        if title is not None:
            payload["title"] = title

        if status is not None:
            valid_status = {"on": "OnTrack", "off": "AtRisk", "complete": "Complete"}
            status_key = status.lower()
            if status_key not in valid_status:
                raise ValueError(
                    "Invalid status value. Must be 'on', 'off', or 'complete'."
                )
            payload["completion"] = valid_status[status_key]

        response = await self._client.put(f"rocks/{goal_id}", json=payload)
        response.raise_for_status()
        return True

    async def archive(self, goal_id: int) -> bool:
        """Archive a rock with the specified goal ID.

        Args:
            goal_id: The ID of the goal/rock to archive

        Returns:
            True if the archival was successful

        """
        response = await self._client.put(f"rocks/{goal_id}/archive")
        response.raise_for_status()
        return True

    async def restore(self, goal_id: int) -> bool:
        """Restore a previously archived goal identified by the provided goal ID.

        Args:
            goal_id: The unique identifier of the goal to restore

        Returns:
            True if the restore operation was successful

        """
        response = await self._client.put(f"rocks/{goal_id}/restore")
        response.raise_for_status()
        return True

    async def _get_archived_goals(
        self, user_id: int | None = None
    ) -> list[ArchivedGoalInfo]:
        """Retrieve all archived goals for a specific user (private method).

        Args:
            user_id: The ID of the user (default is the initialized user ID)

        Returns:
            A list of ArchivedGoalInfo model instances containing archived goal details

        """
        if user_id is None:
            user_id = await self.get_user_id()

        response = await self._client.get(f"archivedrocks/user/{user_id}")
        response.raise_for_status()
        data = response.json()

        return [
            ArchivedGoalInfo(
                id=goal["Id"],
                title=goal["Name"],
                created_at=goal["CreateTime"],
                due_date=goal["DueDate"],
                status="Complete" if goal.get("Complete") else "Incomplete",
            )
            for goal in data
        ]
