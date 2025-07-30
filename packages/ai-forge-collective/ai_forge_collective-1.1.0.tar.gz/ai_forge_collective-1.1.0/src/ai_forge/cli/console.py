"""Console output utilities with Rich integration for AI Forge CLI.

This module provides a centralized console management system with Rich integration,
offering various output methods, progress indicators, and formatted output capabilities.
"""

import logging
import sys
from contextlib import contextmanager
from typing import Any, Generator, Literal, Optional, Union

from rich.console import Capture
from rich.console import Console as RichConsole
from rich.live import Live
from rich.panel import Panel
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TaskID,
    TextColumn,
    TimeElapsedColumn,
)
from rich.spinner import Spinner
from rich.status import Status
from rich.table import Table
from rich.text import Text
from rich.tree import Tree

from ai_forge.exceptions import AIForgeError


class Console:
    """Centralized console management with Rich integration.

    This class wraps Rich console functionality and provides standardized
    output methods for different message types, progress indicators, and
    formatted output components.

    Attributes:
        verbose: Whether verbose mode is enabled
        _console: Internal Rich console instance
        _logger: Logger instance for this console
    """

    def __init__(
        self,
        verbose: bool = False,
        stderr: bool = False,
        color_system: Optional[
            Literal["auto", "standard", "256", "truecolor", "windows"]
        ] = None,
        force_terminal: Optional[bool] = None,
    ) -> None:
        """Initialize Console with Rich integration.

        Args:
            verbose: Enable verbose mode for debug output
            stderr: Write to stderr instead of stdout
            color_system: Force specific color system
                ('auto', 'standard', '256', 'truecolor', None)
            force_terminal: Force terminal detection override
        """
        self.verbose = verbose
        self._console = RichConsole(
            file=sys.stderr if stderr else sys.stdout,
            color_system=color_system,
            force_terminal=force_terminal,
        )
        self._logger = logging.getLogger(__name__)

    def set_verbose(self, verbose: bool) -> None:
        """Update verbose mode setting.

        Args:
            verbose: New verbose mode setting
        """
        self.verbose = verbose
        self._logger.debug("Verbose mode %s", "enabled" if verbose else "disabled")

    def success(self, message: str, **kwargs: Any) -> None:
        """Display a success message with green checkmark.

        Args:
            message: The success message to display
            **kwargs: Additional arguments passed to rich.console.print
        """
        self._console.print(f"✅ {message}", style="bold green", **kwargs)
        if self.verbose:
            self._logger.info("SUCCESS: %s", message)

    def error(
        self, message: str, exception: Optional[Exception] = None, **kwargs: Any
    ) -> None:
        """Display an error message with red styling.

        Args:
            message: The error message to display
            exception: Optional exception for additional context
            **kwargs: Additional arguments passed to rich.console.print
        """
        self._console.print(f"❌ {message}", style="bold red", **kwargs)
        if self.verbose:
            self._logger.error("ERROR: %s", message)

        if exception and self.verbose:
            if isinstance(exception, AIForgeError):
                self._console.print(
                    f"   Error Code: {exception.error_code}", style="red"
                )
                if exception.details:
                    self._console.print(f"   Details: {exception.details}", style="red")
            else:
                self._console.print(
                    f"   Exception: {type(exception).__name__}: {exception}",
                    style="red",
                )

    def warning(self, message: str, **kwargs: Any) -> None:
        """Display a warning message with yellow styling.

        Args:
            message: The warning message to display
            **kwargs: Additional arguments passed to rich.console.print
        """
        self._console.print(f"⚠️  {message}", style="bold yellow", **kwargs)
        if self.verbose:
            self._logger.warning("WARNING: %s", message)

    def info(self, message: str, **kwargs: Any) -> None:
        """Display an info message with blue styling.

        Args:
            message: The info message to display
            **kwargs: Additional arguments passed to rich.console.print
        """
        self._console.print(f"ℹ️  {message}", style="bold blue", **kwargs)
        if self.verbose:
            self._logger.info("INFO: %s", message)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Display a debug message with gray styling (only in verbose mode).

        Args:
            message: The debug message to display
            **kwargs: Additional arguments passed to rich.console.print
        """
        if self.verbose:
            self._console.print(f"🔍 {message}", style="dim", **kwargs)
        self._logger.debug("DEBUG: %s", message)

    def print(self, *args: Any, **kwargs: Any) -> None:
        """Print using the underlying Rich console.

        Args:
            *args: Arguments passed to rich.console.print
            **kwargs: Keyword arguments passed to rich.console.print
        """
        self._console.print(*args, **kwargs)

    def rule(self, title: Optional[str] = None, **kwargs: Any) -> None:
        """Print a horizontal rule with optional title.

        Args:
            title: Optional title for the rule
            **kwargs: Additional arguments passed to rich.console.rule
        """
        self._console.rule(title or "", **kwargs)

    def panel(
        self,
        content: Union[str, Text],
        title: Optional[str] = None,
        title_align: Literal["left", "center", "right"] = "left",
        border_style: str = "blue",
        **kwargs: Any,
    ) -> None:
        """Display content in a panel with optional title and styling.

        Args:
            content: Content to display in the panel
            title: Optional panel title
            title_align: Title alignment ('left', 'center', 'right')
            border_style: Border color/style
            **kwargs: Additional arguments passed to rich.panel.Panel
        """
        panel = Panel(
            content,
            title=title,
            title_align=title_align,
            border_style=border_style,
            **kwargs,
        )
        self._console.print(panel)

    def table(self, title: Optional[str] = None) -> Table:
        """Create a new Rich table for formatted output.

        Args:
            title: Optional table title

        Returns:
            A Rich Table instance ready for configuration
        """
        return Table(title=title, show_header=True, header_style="bold magenta")

    def tree(self, label: str, **kwargs: Any) -> Tree:
        """Create a new Rich tree for hierarchical display.

        Args:
            label: Root label for the tree
            **kwargs: Additional arguments passed to rich.tree.Tree

        Returns:
            A Rich Tree instance ready for configuration
        """
        return Tree(label, **kwargs)

    @contextmanager
    def status(
        self,
        message: str,
        spinner: str = "dots",
        spinner_style: str = "status.spinner",
    ) -> Generator[Status, None, None]:
        """Context manager for displaying a status spinner.

        Args:
            message: Status message to display
            spinner: Spinner style name
            spinner_style: Rich style for the spinner

        Yields:
            Status instance for updates during operation

        Example:
            with console.status("Processing files...") as status:
                # Do work
                status.update("Still processing...")
                # More work
        """
        status = Status(message, spinner=spinner, spinner_style=spinner_style)
        try:
            status.start()
            yield status
        finally:
            status.stop()

    @contextmanager
    def progress(
        self,
        description: str = "Progress",
        show_percentage: bool = True,
        show_time_elapsed: bool = True,
        show_eta: bool = False,
    ) -> Generator[tuple[Progress, TaskID], None, None]:
        """Context manager for displaying a progress bar.

        Args:
            description: Description for the progress bar
            show_percentage: Show completion percentage
            show_time_elapsed: Show elapsed time
            show_eta: Show estimated time to completion

        Yields:
            Tuple of (Progress instance, TaskID) for tracking progress

        Example:
            with console.progress("Processing files") as (progress, task_id):
                total = len(files)
                progress.update(task_id, total=total)
                for i, file in enumerate(files):
                    # Process file
                    progress.update(task_id, advance=1)
        """
        columns = [
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            MofNCompleteColumn(),
        ]

        if show_percentage:
            columns.append(TextColumn("[progress.percentage]{task.percentage:>3.0f}%"))

        if show_time_elapsed:
            columns.append(TimeElapsedColumn())

        progress = Progress(*columns, console=self._console)
        task_id = progress.add_task(description, total=None)

        try:
            progress.start()
            yield progress, task_id
        finally:
            progress.stop()

    @contextmanager
    def spinner(
        self, message: str, spinner_style: str = "dots", text_style: str = "status.text"
    ) -> Generator[None, None, None]:
        """Context manager for displaying a simple spinner.

        Args:
            message: Message to display with spinner
            spinner_style: Spinner animation style
            text_style: Rich style for the text

        Example:
            with console.spinner("Loading configuration..."):
                # Do work that takes time
                config = load_config()
        """
        spinner = Spinner(spinner_style, text=message, style=text_style)

        with Live(spinner, console=self._console, refresh_per_second=10):
            yield

    @contextmanager
    def capture(self) -> Generator[Capture, None, None]:
        """Context manager to capture console output.

        Yields:
            Capture object with get() method to retrieve captured output

        Example:
            with console.capture() as captured:
                console.info("This will be captured")
                console.success("This too")
            output = captured.get()
        """
        with self._console.capture() as capture:
            yield capture

    def clear(self) -> None:
        """Clear the console screen."""
        self._console.clear()

    def save_text(self, path: str, clear: bool = True, styles: bool = False) -> None:
        """Save console contents to a text file.

        Args:
            path: File path to save to
            clear: Clear console after saving
            styles: Include Rich styling in saved text
        """
        try:
            self._console.save_text(path, clear=clear, styles=styles)
            self._logger.debug("Console output saved to %s", path)
        except Exception as e:
            self._logger.error("Failed to save console output to %s: %s", path, e)
            raise

    def save_html(
        self, path: str, clear: bool = True, inline_styles: bool = False
    ) -> None:
        """Save console contents to an HTML file.

        Args:
            path: File path to save to
            clear: Clear console after saving
            inline_styles: Use inline CSS styles instead of classes
        """
        try:
            self._console.save_html(path, clear=clear, inline_styles=inline_styles)
            self._logger.debug("Console output saved as HTML to %s", path)
        except Exception as e:
            self._logger.error(
                "Failed to save console output as HTML to %s: %s", path, e
            )
            raise

    @property
    def size(self) -> tuple[int, int]:
        """Get console size as (width, height)."""
        return self._console.size

    @property
    def is_terminal(self) -> bool:
        """Check if output is to a terminal."""
        return self._console.is_terminal

    @property
    def is_jupyter(self) -> bool:
        """Check if running in Jupyter environment."""
        return self._console.is_jupyter


# Global console instance for use throughout the application
# This can be imported and used directly, or replaced with a custom instance
console = Console()


# Context manager for temporarily setting verbose mode
@contextmanager
def verbose_mode(enabled: bool = True) -> Generator[None, None, None]:
    """Context manager to temporarily enable/disable verbose mode.

    Args:
        enabled: Whether to enable verbose mode in this context

    Example:
        with verbose_mode(True):
            console.debug("This will be shown even if global verbose is False")
    """
    original_verbose = console.verbose
    try:
        console.set_verbose(enabled)
        yield
    finally:
        console.set_verbose(original_verbose)


# Convenience functions for quick access to common operations
def print_success(message: str, **kwargs: Any) -> None:
    """Convenience function for success messages."""
    console.success(message, **kwargs)


def print_error(
    message: str, exception: Optional[Exception] = None, **kwargs: Any
) -> None:
    """Convenience function for error messages."""
    console.error(message, exception=exception, **kwargs)


def print_warning(message: str, **kwargs: Any) -> None:
    """Convenience function for warning messages."""
    console.warning(message, **kwargs)


def print_info(message: str, **kwargs: Any) -> None:
    """Convenience function for info messages."""
    console.info(message, **kwargs)


def print_debug(message: str, **kwargs: Any) -> None:
    """Convenience function for debug messages."""
    console.debug(message, **kwargs)
