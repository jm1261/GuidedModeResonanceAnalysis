from __future__ import annotations

import argparse
from pathlib import Path


LOG_FILE_PREFIX = "application_"
RETAIN_MARKERS = ("ERROR", "WARNING", "FAILURE", "FAILED")


def contains_retain_marker(log_file: Path) -> bool:
    """
    Function Details
    ================
    Return whether a log file contains a marker that should retain it.

    Parameters
    ----------
    log_file: Path
        Log file to inspect.

    Returns
    -------
    bool
    ``True`` when the file contains any configured retention marker:
    ``ERROR``, ``WARNING``, ``FAILURE``, or ``FAILED``.

    Raises
    ------
    OSError: If the file cannot be read.
    """
    contents = log_file.read_text(encoding="utf-8", errors="replace").upper()
    return any(marker in contents for marker in RETAIN_MARKERS)


def cleanup_logs(log_directory: Path, dry_run: bool = False) -> tuple[int, int]:
    """
    Function Details
    ================
    Delete clean application logs and report deleted and retained counts.

    Parameters
    ----------
    log_directory: Path
        Directory containing files whose names begin with ``application_``.
    dry_run: bool
        When ``True``, report deletions without removing files.

    Returns
    -------
    tuple[int, int]
        Number of deleted files, or files that would be deleted in dry-run
        mode, followed by the number of retained files.

    Side Effects
    ------------
    Prints one status line for each processed file.

    Raises
    ------
    OSError: If a matching file cannot be inspected or deleted.
    """
    deleted = 0
    retained = 0

    for log_file in sorted(log_directory.glob(f"{LOG_FILE_PREFIX}*")):
        if not log_file.is_file():
            continue

        if contains_retain_marker(log_file):
            retained += 1
            print(f"Retained: {log_file.name}")
            continue

        if not dry_run:
            log_file.unlink()
        deleted += 1
        action = "Would delete" if dry_run else "Deleted"
        print(f"{action}: {log_file.name}")

    return deleted, retained


def main() -> None:
    """
    Function Details
    ================
    Parse options and run cleanup in this directory.

    Returns
    -------
    None

    Raises
    ------
    OSError: If a matching log file cannot be inspected or deleted.
    SystemExit: If command-line arguments are invalid.

    Side Effects
    ------------
    Runs ``cleanup_logs`` in the logging directory, which may delete matching
    files and print per-file status lines, then prints the result summary.

    """
    parser = argparse.ArgumentParser(
        description="Delete application log files without errors or failure warnings."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="List files that would be deleted without removing them.",
    )
    args = parser.parse_args()

    log_directory = Path(__file__).resolve().parent
    deleted, retained = cleanup_logs(log_directory, dry_run=args.dry_run)
    action = "would be deleted" if args.dry_run else "deleted"
    print(f"{deleted} file(s) {action}; {retained} file(s) retained.")


if __name__ == "__main__":
    main()