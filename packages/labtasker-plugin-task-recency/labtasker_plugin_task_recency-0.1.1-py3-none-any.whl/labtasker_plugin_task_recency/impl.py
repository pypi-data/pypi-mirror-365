from datetime import timedelta
from enum import Enum

from labtasker.client.core.api import ls_tasks


class By(str, Enum):
    created_at = "created_at"
    start_time = "start_time"
    last_heartbeat = "last_heartbeat"
    last_modified = "last_modified"


def get_kth_recent_tasks(by: By, order: str, k: int, interval: float):
    """
    Get tasks from the kth most recent time chunk, where chunks are formed by
    grouping tasks with time differences less than the specified interval.

    Args:
        by: Attribute to sort and chunk by (created_at, start_time, etc.)
        order: Sort order ("asc" or "desc")
        k: Which chunk to retrieve (1 is the most recent chunk, 2 is the second, etc.)
        interval: Maximum time gap in seconds between tasks in the same chunk

    Returns:
        List of tasks in the kth chunk
    """
    if k < 1:
        raise ValueError("k must be at least 1")

    offset = 0
    limit = 100  # Only used for pagination

    # Current chunk counter (1-based)
    current_chunk = 1
    current_tasks = []
    prev_time = None
    interval_delta = timedelta(seconds=interval)

    while True:
        new = ls_tasks(
            limit=limit, offset=offset, sort=[(by, -1 if order == "desc" else 1)]
        ).content

        if not new:  # No more tasks to process
            break

        for task in new:
            current_time = getattr(task, by)

            # Initialize with the first task
            if prev_time is None:
                prev_time = current_time
                current_tasks.append(task)
                continue

            # Check if this task belongs to a new chunk
            if abs(current_time - prev_time) > interval_delta:
                # We've found the end of a chunk
                if current_chunk == k:
                    # This is the kth chunk we're looking for, return it
                    return current_tasks

                # Move to the next chunk
                current_chunk += 1
                current_tasks = [task]  # Start the new chunk with this task
            else:
                # Same chunk, add the task
                current_tasks.append(task)

            prev_time = current_time

        # Prepare for the next page of results
        offset += limit

    # If we get here, and we're on the kth chunk, return it
    if current_chunk == k:
        return current_tasks

    # We've processed all tasks but didn't find k chunks
    return []
