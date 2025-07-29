import typer
import os
from pathlib import Path
import dateutil.parser
import dateutil.tz
from git import Repo, Commit
from typing_extensions import Annotated
from .utils import (
    make_backup_branch,
    parse_datetime_str,
    parse_time_str,
    remap,
    fmt,
)
import datetime
from businesstimedelta import BusinessTimeDelta, WorkDayRule

local_tz = dateutil.tz.tzlocal()


Commit.min_datetime = property(
    lambda self: min(self.authored_datetime, self.committed_datetime)
)
Commit.max_datetime = property(
    lambda self: max(self.authored_datetime, self.committed_datetime)
)


def redate(
    base_ref: Annotated[
        str,
        typer.Argument(
            help="Base ref at which redating starts. If empty, will redate the last commit only. Set `root` the redate the whole history.",
        ),
    ] = "HEAD~1",
    min_date: Annotated[
        datetime.datetime | None,
        typer.Option(
            help="Custom start date and time",
            parser=parse_datetime_str,
            metavar="YYYY-MM-DD(THH:MM(:SS))",
        ),
    ] = None,
    max_date: Annotated[
        datetime.datetime | None,
        typer.Option(
            help="Custom end date and time",
            parser=parse_datetime_str,
            metavar="YYYY-MM-DD(THH:MM(:SS))",
        ),
    ] = None,
    working_days: Annotated[
        # TODO: once https://github.com/fastapi/typer/pull/800 is merged, switch to list[int] with separator ","
        str,
        typer.Option(
            help="Working days, provide this argument for each working day (monday=1)",
        ),
    ] = "1,2,3,4,5",
    working_hour_start: Annotated[
        # TODO: try to create a datetime.time type
        str,
        typer.Option(
            help="Work day starting hour",
            metavar="HH:MM(:SS)",
        ),
    ] = "8:00",
    working_hour_end: Annotated[
        # TODO: try to create a datetime.time type
        str,
        typer.Option(
            help="Work day ending hour",
            metavar="HH:MM(:SS)",
        ),
    ] = "18:00",
    repository: Annotated[
        Path,
        typer.Option(help="Path to the git repository"),
    ] = Path("."),
):
    repo = Repo(repository)
    current_commit = repo.head.commit
    if base_ref == "root":
        commit_range = "HEAD"
        rebase_ref = "--root"
    else:
        commit_range = f"{base_ref}..HEAD"
        rebase_ref = base_ref
    print(f"Will redate range {commit_range}")

    # Make a backup branch if needed
    make_backup_branch(repo)

    # Setup the rules
    work_rule = WorkDayRule(
        start_time=parse_time_str(working_hour_start),
        end_time=parse_time_str(working_hour_end),
        working_days=[int(d) - 1 for d in working_days.split(",")],
    )

    # Get date ranges
    print()
    commits = list(repo.iter_commits(commit_range))

    if not commits:
        raise RuntimeError(f"The given range (`{commit_range}`) is empty")

    old_min_date = min(c.min_datetime for c in commits)
    old_max_date = max(c.max_datetime for c in commits)
    print(f"Old range: {fmt(old_min_date)} - {fmt(old_max_date)}")
    new_min_date = min_date or old_min_date
    new_max_date = max_date or old_max_date
    print(f"New range: {fmt(new_min_date)} - {fmt(new_max_date)}")
    new_working_range = work_rule.difference(new_min_date, new_max_date)
    new_working_seconds = new_working_range.hours * 3600 + new_working_range.seconds

    # Min rebase
    os.environ["GIT_SEQUENCE_EDITOR"] = "python -m gitredate edit-todo"
    repo.git.rebase("--interactive", rebase_ref)

    # Ammend each commit
    print()
    while True:
        rebase_commit = repo.commit("REBASE_HEAD")
        is_last = rebase_commit == current_commit

        old_date = rebase_commit.min_datetime
        if old_min_date == old_max_date:
            working_seconds = 0
        else:
            working_seconds = remap(
                old_date, old_min_date, old_max_date, 0, new_working_seconds
            )
        new_date = new_min_date + BusinessTimeDelta(work_rule, seconds=working_seconds)
        print(
            f"Redating {rebase_commit.hexsha[:7]}:    {fmt(old_date)} → {fmt(new_date)}"
        )
        repo.git.commit(
            "--amend",
            "--no-edit",
            f'--date="{new_date}"',
            env={"GIT_COMMITTER_DATE": str(new_date)},
        )
        repo.git.rebase("--continue")
        if is_last:
            break
