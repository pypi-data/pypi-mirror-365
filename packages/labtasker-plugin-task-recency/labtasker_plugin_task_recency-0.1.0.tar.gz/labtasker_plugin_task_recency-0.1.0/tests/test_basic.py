import os
import time
from contextlib import suppress

import pytest
from typer.testing import CliRunner

from labtasker import (
    LabtaskerNetworkError,
    create_queue,
    delete_queue,
    get_client_config,
    submit_task,
)
from labtasker_plugin_task_recency.main import By, get_kth_recent_tasks

runner = CliRunner()


@pytest.fixture(scope="module", autouse=True)
def setup_tasks():
    print(f"Current working directory: {os.getcwd()}")
    # 1. try to create queue
    with suppress(LabtaskerNetworkError):
        delete_queue(cascade_delete=True)

    config = get_client_config()
    create_queue(
        queue_name=config.queue.queue_name,
        password=config.queue.password.get_secret_value(),
    )

    # 2. submit tasks
    for i in range(5):
        for j in range(10):
            submit_task(
                task_name=f"task_{i}_{j}",
                args={"i": i, "j": j},
            )
        time.sleep(5.0)


def test_first_chunk():
    """Test retrieving the first (most recent) chunk."""
    first_chunk = get_kth_recent_tasks(By.created_at, "desc", 1, 4)
    # Should contain the last batch of tasks (i=4)
    assert len(first_chunk) == 10
    for task in first_chunk:
        assert task.task_name.startswith("task_4_")


def test_second_chunk():
    """Test retrieving the second chunk."""
    second_chunk = get_kth_recent_tasks(By.created_at, "desc", 2, 4)
    # Should contain the second-to-last batch (i=3)
    assert len(second_chunk) == 10
    for task in second_chunk:
        assert task.task_name.startswith("task_3_")


def test_third_chunk():
    """Test retrieving the third chunk."""
    third_chunk = get_kth_recent_tasks(By.created_at, "desc", 3, 4)
    # Should contain the third-to-last batch (i=2)
    assert len(third_chunk) == 10
    for task in third_chunk:
        assert task.task_name.startswith("task_2_")


def test_merged_chunks():
    """Test with a larger interval that should merge chunks."""
    merged_chunks = get_kth_recent_tasks(By.created_at, "desc", 1, 10)
    # Should contain the last two batches (i=3 and i=4)
    assert len(merged_chunks) > 10


def test_small_interval():
    """Test with a very small interval that should split chunks."""
    small_interval = get_kth_recent_tasks(By.created_at, "desc", 1, 0.001)
    # Should contain fewer tasks than a full batch
    assert len(small_interval) < 10

    # Verify all tasks are from the same batch
    batch_prefix = small_interval[0].task_name.split("_")[1]
    for task in small_interval:
        assert task.task_name.split("_")[1] == batch_prefix


def test_non_existent_chunk():
    """Test retrieving a non-existent chunk."""
    non_existent = get_kth_recent_tasks(By.created_at, "desc", 10, 4)
    # Should return an empty list
    assert len(non_existent) == 0


def test_ascending_order():
    """Test with ascending order."""
    asc_order = get_kth_recent_tasks(By.created_at, "asc", 1, 4)
    # Should contain the first batch of tasks (i=0)
    assert len(asc_order) == 10
    for task in asc_order:
        assert task.task_name.startswith("task_0_")


def test_all_chunks_exist():
    """Test that all 5 expected chunks exist."""
    for i in range(1, 6):
        chunk = get_kth_recent_tasks(By.created_at, "desc", i, 4)
        expected_i = 5 - i
        assert len(chunk) == 10
        for task in chunk:
            assert task.task_name.startswith(f"task_{expected_i}_")
