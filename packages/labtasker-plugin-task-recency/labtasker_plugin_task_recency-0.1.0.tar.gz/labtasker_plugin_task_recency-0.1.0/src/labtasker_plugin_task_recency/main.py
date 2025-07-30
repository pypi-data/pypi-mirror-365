import typer

from labtasker.client.cli.task import app
from labtasker.client.core.cli_utils import cli_utils_decorator
from labtasker.client.core.logging import stdout_console
from labtasker.utils import parse_time_interval
from labtasker_plugin_task_recency.impl import By, get_kth_recent_tasks


def validate_order(order: str):
    if order not in ["asc", "desc"]:
        raise typer.BadParameter(f"Invalid order: {order}")
    return order


@app.command()
@cli_utils_decorator
def recent(
    by: By = typer.Option(By.created_at, help="Group tasks by a specific field."),
    interval: str = typer.Option(
        "5s",
        "--interval",
        "-i",
        help="Interval to group tasks by. "
        "Accepts a duration string (e.g. '1h', '1h30m', '50s'). "
        "Defaults to 1 hour.",
    ),
    k: int = typer.Option(
        1, "--k", "-k", min=1, help="The k-th recent group of tasks."
    ),
    order: str = typer.Option(
        "desc",
        "--order",
        callback=validate_order,
        help="Order to sort tasks in each group. "
        "Accepts 'asc' or 'desc'. Defaults to 'desc'. desc: recent; asc: least recent.",
    ),
):
    """"""
    interval = parse_time_interval(interval)
    tasks = get_kth_recent_tasks(by, order, k, interval)

    for task in tasks:
        stdout_console.print(task.task_id)
