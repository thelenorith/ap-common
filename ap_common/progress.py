"""
Progress indicator utilities for long-running operations.

Provides a consistent, reusable interface for showing progress in CLI tools
that process files and folders. Built on tqdm for terminal-friendly output.

Example usage in external tools:

    from ap_common.progress import progress_iter, ProgressTracker

    # Simple iteration with progress bar
    for filename in progress_iter(filenames, desc="Moving files", enabled=show_progress):
        move_file(filename, dest)

    # With dynamic status updates
    with ProgressTracker(filenames, desc="Processing", enabled=show_progress) as tracker:
        for filename in tracker:
            tracker.set_status(f"Current: {os.path.basename(filename)}")
            process_file(filename)

    # For operations where total is unknown upfront
    tracker = ProgressTracker(desc="Scanning directories", enabled=show_progress)
    tracker.start()
    for item in some_generator():
        tracker.update(status=item.name)
    tracker.finish()
"""

from tqdm import tqdm


def progress_iter(
    iterable,
    desc: str = "Processing",
    unit: str = "files",
    enabled: bool = True,
    total: int = None,
):
    """
    Wrap an iterable with a progress bar.

    This is the simplest way to add progress indication to any loop.
    When disabled, returns the iterable unchanged (zero overhead).

    Args:
        iterable: Any iterable to wrap
        desc: Description shown before the progress bar
        unit: Unit name shown in progress stats (e.g., "files", "dirs")
        enabled: Whether to show progress (False = passthrough)
        total: Total count if known (auto-detected for sequences)

    Returns:
        Iterator that yields items from the iterable

    Example:
        for f in progress_iter(files, desc="Copying", enabled=verbose):
            copy_file(f, dest)
    """
    if not enabled:
        return iterable

    return tqdm(iterable, desc=desc, unit=unit, total=total)


class ProgressTracker:
    """
    A flexible progress tracker for operations needing dynamic updates.

    Use this when you need to update the progress bar's status/description
    during iteration, or when the total count isn't known upfront.

    Can be used as a context manager or manually controlled.

    Args:
        iterable: Optional iterable to track (can be None for manual mode)
        desc: Description shown before the progress bar
        unit: Unit name shown in progress stats
        enabled: Whether to show progress (False = no-op)
        total: Total count if known

    Example as context manager:
        with ProgressTracker(files, desc="Processing") as tracker:
            for f in tracker:
                tracker.set_status(os.path.basename(f))
                process(f)

    Example manual mode:
        tracker = ProgressTracker(desc="Scanning")
        tracker.start()
        for item in generator():
            tracker.update(status=item.name)
        tracker.finish()
    """

    def __init__(
        self,
        iterable=None,
        desc: str = "Processing",
        unit: str = "files",
        enabled: bool = True,
        total: int = None,
    ):
        self.iterable = iterable
        self.desc = desc
        self.unit = unit
        self.enabled = enabled
        self.total = total
        self._pbar = None
        self._iterator = None

    def start(self):
        """Start the progress bar (for manual mode)."""
        if self.enabled:
            self._pbar = tqdm(
                total=self.total,
                desc=self.desc,
                unit=self.unit,
            )

    def update(self, n: int = 1, status: str = None):
        """
        Update progress by n steps and optionally set status text.

        Args:
            n: Number of steps to advance (default 1)
            status: Optional status text to display
        """
        if self._pbar is not None:
            if status is not None:
                self._pbar.set_postfix_str(status)
            self._pbar.update(n)

    def set_status(self, status: str):
        """
        Set the status text shown after the progress bar.

        Args:
            status: Status text (e.g., current filename being processed)
        """
        if self._pbar is not None:
            self._pbar.set_postfix_str(status)

    def set_description(self, desc: str):
        """
        Update the description shown before the progress bar.

        Args:
            desc: New description text
        """
        if self._pbar is not None:
            self._pbar.set_description(desc)

    def finish(self):
        """Close the progress bar (for manual mode)."""
        if self._pbar is not None:
            self._pbar.close()
            self._pbar = None

    def __enter__(self):
        """Context manager entry - starts progress bar."""
        if self.enabled and self.iterable is not None:
            self._pbar = tqdm(
                self.iterable,
                desc=self.desc,
                unit=self.unit,
                total=self.total,
            )
            self._iterator = iter(self._pbar)
        elif self.iterable is not None:
            self._iterator = iter(self.iterable)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit - closes progress bar."""
        if self._pbar is not None:
            self._pbar.close()
            self._pbar = None
        return False

    def __iter__(self):
        """Iterate over the wrapped iterable."""
        if self._iterator is not None:
            return self
        if not self.enabled:
            return iter(self.iterable) if self.iterable else iter([])
        return iter(
            tqdm(
                self.iterable if self.iterable else [],
                desc=self.desc,
                unit=self.unit,
                total=self.total,
            )
        )

    def __next__(self):
        """Get next item from the iterator."""
        if self._iterator is None:
            raise StopIteration
        return next(self._iterator)
