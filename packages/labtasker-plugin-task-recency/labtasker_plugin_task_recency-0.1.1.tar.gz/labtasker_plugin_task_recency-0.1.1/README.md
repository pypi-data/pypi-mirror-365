# labtasker-plugin-task-recency

A Labtasker plugin for retrieving tasks grouped by time chunks.

## Overview

This plugin extends Labtasker's functionality by allowing you to retrieve tasks that occurred within specific time
chunks. It groups tasks based on time intervals between consecutive tasks, making it easy to analyze and process tasks
that were submitted in bursts.

## Installation

```bash
pip install labtasker-plugin-task-recency
```

## Usage

```bash
labtasker task recent [OPTIONS]
```

### Options

| Option           | Default      | Description                                                                                                   |
|------------------|--------------|---------------------------------------------------------------------------------------------------------------|
| `--by`           | `created_at` | The timestamp field to group tasks by. Options: `created_at`, `start_time`, `last_heartbeat`, `last_modified` |
| `--interval, -i` | `5s`         | Time interval to define chunks. Accepts duration strings like `1h`, `1h30m`, `50s`                            |
| `--k, -k`        | `1`          | Which chunk to retrieve (1 is most recent, 2 is second most recent, etc.)                                     |
| `--order`        | `desc`       | Sort order within each chunk. Options: `desc` (newest first), `asc` (oldest first)                            |

### Examples

1. Get the most recent batch of tasks (tasks submitted with less than 5 seconds between them):
   ```bash
   labtasker task recent
   ```

2. Get the second most recent batch of tasks:
   ```bash
   labtasker task recent --k 2
   ```

3. Get tasks grouped by a 1-hour interval:
   ```bash
   labtasker task recent --interval 1h
   ```

4. Get tasks grouped by their start time instead of creation time:
   ```bash
   labtasker task recent --by start_time
   ```

5. Get the oldest batch of tasks:
   ```bash
   labtasker task recent --k 1 --order asc
   ```

## How It Works

The plugin groups tasks into "chunks" based on the time gaps between consecutive tasks. If two tasks are submitted with
a gap smaller than the specified interval, they belong to the same chunk. When the time gap exceeds the interval, a new
chunk begins.

This approach is useful for identifying batches of tasks that were submitted together, allowing for easier management
and analysis of task patterns.

## Use Cases

- Batch delete / update of most recently submitted tasks
   ```bash
  labtasker task recent | labtasker task delete -y
   ```