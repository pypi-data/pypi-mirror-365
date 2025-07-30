"""Error handling and exit code management for AI Forge CLI.

This module provides comprehensive error handling capabilities including:
- Standard CLI exit codes following Unix conventions
- Error handler decorator for Click commands
- User-friendly error messages with debug mode support
- Proper exception mapping and resource cleanup
"""

import functools
import logging
import sys
import traceback
from typing import Any, Callable, Optional, TypeVar

import click

from ai_forge.cli.console import console
from ai_forge.exceptions import (
    AIForgeError,
    ConfigurationError,
    DependencyError,
    FileSystemError,
    TemplateError,
    ValidationError,
)

# Type variable for decorated functions
F = TypeVar("F", bound=Callable[..., Any])


class ExitCode:
    """Standard CLI exit codes following Unix conventions.

    These exit codes provide consistent error reporting across all AI Forge
    CLI commands and help with automation and scripting.
    """

    SUCCESS = 0  # Command completed successfully
    GENERAL_ERROR = 1  # General catch-all error
    MISUSE = 2  # Misuse of shell command (e.g., invalid arguments)
    CONFIGURATION_ERROR = 3  # Configuration file issues
    TEMPLATE_ERROR = 4  # Template processing errors
    VALIDATION_ERROR = 5  # Input validation failures
    FILESYSTEM_ERROR = 6  # File system operation errors
    DEPENDENCY_ERROR = 7  # Missing or incompatible dependencies
    PERMISSION_ERROR = 8  # Permission denied errors
    NETWORK_ERROR = 9  # Network-related errors
    INTERRUPTED = 130  # Process interrupted (Ctrl+C)


# Exception to exit code mapping
EXCEPTION_EXIT_CODES: dict[type[BaseException], int] = {
    ConfigurationError: ExitCode.CONFIGURATION_ERROR,
    TemplateError: ExitCode.TEMPLATE_ERROR,
    ValidationError: ExitCode.VALIDATION_ERROR,
    FileSystemError: ExitCode.FILESYSTEM_ERROR,
    DependencyError: ExitCode.DEPENDENCY_ERROR,
    PermissionError: ExitCode.PERMISSION_ERROR,
    OSError: ExitCode.FILESYSTEM_ERROR,
    KeyboardInterrupt: ExitCode.INTERRUPTED,
    click.ClickException: ExitCode.MISUSE,
    click.Abort: ExitCode.INTERRUPTED,
}


def get_exit_code(exception: BaseException) -> int:
    """Get appropriate exit code for an exception.

    Args:
        exception: The exception to map to an exit code

    Returns:
        Appropriate exit code for the exception type
    """
    # Check for exact type match first
    exception_type = type(exception)
    if exception_type in EXCEPTION_EXIT_CODES:
        return EXCEPTION_EXIT_CODES[exception_type]

    # Check for inheritance-based matches
    for exc_type, exit_code in EXCEPTION_EXIT_CODES.items():
        if isinstance(exception, exc_type):
            return exit_code

    # Default to general error
    return ExitCode.GENERAL_ERROR


def format_error_message(exception: BaseException, verbose: bool = False) -> str:
    """Format an exception into a user-friendly error message.

    Args:
        exception: The exception to format
        verbose: Whether to include additional debug information

    Returns:
        Formatted error message string
    """
    if isinstance(exception, AIForgeError):
        message = str(exception)

        if verbose and exception.details:
            details_str = ", ".join(f"{k}={v}" for k, v in exception.details.items())
            message += f" (Details: {details_str})"

        return message

    elif isinstance(exception, click.ClickException):
        # Let Click handle its own exceptions
        return str(exception)

    elif isinstance(exception, KeyboardInterrupt):
        return "Operation cancelled by user"

    elif isinstance(exception, PermissionError):
        return f"Permission denied: {exception}"

    elif isinstance(exception, FileNotFoundError):
        return f"File not found: {exception.filename or 'unknown file'}"

    elif isinstance(exception, OSError):
        return f"System error: {exception}"

    else:
        # Generic exception formatting
        exc_name = type(exception).__name__
        return f"{exc_name}: {exception}" if str(exception) else exc_name


def get_error_suggestions(exception: BaseException) -> list[str]:
    """Get helpful suggestions for common errors.

    Args:
        exception: The exception to provide suggestions for

    Returns:
        List of suggestion strings for fixing the error
    """
    suggestions: list[str] = []

    if isinstance(exception, ConfigurationError):
        suggestions.extend(
            [
                "Check your configuration file syntax (YAML/JSON)",
                "Verify all required configuration parameters are present",
                "Run 'ai-forge validate' to check configuration",
            ]
        )

    elif isinstance(exception, TemplateError):
        suggestions.extend(
            [
                "Verify the template exists and is readable",
                "Check template syntax for errors",
                "Ensure all required template variables are provided",
            ]
        )

    elif isinstance(exception, ValidationError):
        suggestions.extend(
            [
                "Check your input parameters for correct format",
                "Review command usage with --help",
                "Verify file paths and permissions",
            ]
        )

    elif isinstance(exception, FileSystemError):
        suggestions.extend(
            [
                "Check file and directory permissions",
                "Verify paths exist and are accessible",
                "Ensure sufficient disk space",
            ]
        )

    elif isinstance(exception, DependencyError):
        suggestions.extend(
            [
                "Install missing dependencies with 'uv add <package>'",
                "Check version compatibility requirements",
                "Verify your Python environment is activated",
            ]
        )

    elif isinstance(exception, PermissionError):
        suggestions.extend(
            [
                "Check file and directory permissions",
                "Try running with appropriate privileges",
                "Verify you have write access to the target location",
            ]
        )

    elif isinstance(exception, FileNotFoundError):
        suggestions.extend(
            [
                "Verify the file path is correct",
                "Check if the file exists",
                "Ensure you're in the correct directory",
            ]
        )

    elif isinstance(exception, KeyboardInterrupt):
        suggestions.append("Use Ctrl+C to safely interrupt operations")

    return suggestions


def display_error(
    exception: BaseException, verbose: bool = False, show_suggestions: bool = True
) -> None:
    """Display a formatted error message to the user.

    Args:
        exception: The exception to display
        verbose: Whether to show debug information
        show_suggestions: Whether to show helpful suggestions
    """
    # Format and display the main error message
    message = format_error_message(exception, verbose=verbose)
    console.error(
        message,
        exception=exception if verbose and isinstance(exception, Exception) else None,
    )

    # Show full traceback in verbose mode for non-AIForge exceptions
    if verbose and not isinstance(exception, (AIForgeError, click.ClickException)):
        console.print("\n[dim]Full traceback:[/dim]")
        console.print(traceback.format_exc(), style="dim")

    # Show helpful suggestions
    if show_suggestions:
        suggestions = get_error_suggestions(exception)
        if suggestions:
            console.print("\n[bold blue]Suggestions:[/bold blue]")
            for suggestion in suggestions:
                console.print(f"  • {suggestion}", style="blue")


def handle_errors(func: F) -> F:
    """Decorator to handle errors in CLI commands with proper exit codes.

    This decorator should be applied to all Click command functions to ensure
    consistent error handling and exit code management throughout the CLI.

    Features:
    - Catches all exceptions and maps them to appropriate exit codes
    - Displays user-friendly error messages
    - Shows debug information in verbose mode
    - Provides helpful suggestions for common errors
    - Ensures proper resource cleanup

    Args:
        func: The Click command function to decorate

    Returns:
        Decorated function with error handling

    Example:
        @click.command()
        @handle_errors
        def my_command():
            # Command implementation
            pass
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> None:
        """Wrapper function that handles errors and sets exit codes."""
        ctx = None
        verbose = False
        logger = logging.getLogger(__name__)

        try:
            # Try to get Click context and verbose setting
            try:
                ctx = click.get_current_context()
                if ctx and ctx.obj:
                    verbose = ctx.obj.get("verbose", False)
            except RuntimeError:
                # No Click context available, continue with defaults
                pass

            # Execute the original function
            logger.debug("Executing command: %s", func.__name__)
            result = func(*args, **kwargs)

            # Command completed successfully
            logger.debug("Command completed successfully: %s", func.__name__)
            return result

        except click.ClickException:
            # Let Click handle its own exceptions (they have their own exit logic)
            logger.debug("Click exception in command %s, re-raising", func.__name__)
            raise

        except KeyboardInterrupt as e:
            # Handle user interruption gracefully
            logger.info("Command interrupted by user: %s", func.__name__)
            display_error(e, verbose=verbose, show_suggestions=False)
            sys.exit(ExitCode.INTERRUPTED)

        except Exception as e:
            # Handle all other exceptions
            exit_code = get_exit_code(e)
            logger.error(
                "Command failed: %s, exception: %s, exit_code: %d",
                func.__name__,
                type(e).__name__,
                exit_code,
            )

            # Display error to user
            display_error(e, verbose=verbose)

            # Perform cleanup if needed
            try:
                _cleanup_on_error(ctx)
            except Exception as cleanup_error:
                logger.warning("Error during cleanup: %s", cleanup_error)
                if verbose:
                    console.warning(f"Cleanup error: {cleanup_error}")

            # Exit with appropriate code
            sys.exit(exit_code)

    return wrapper  # type: ignore


def _cleanup_on_error(ctx: Optional[click.Context]) -> None:
    """Perform cleanup operations when an error occurs.

    Args:
        ctx: Optional Click context for accessing shared resources
    """
    logger = logging.getLogger(__name__)

    try:
        # Close any open file handles
        # (In a more complete implementation, this would track open resources)

        # Log cleanup completion
        logger.debug("Error cleanup completed")

    except Exception as e:
        logger.warning("Failed to complete error cleanup: %s", e)
        raise


def safe_exit(exit_code: int = ExitCode.SUCCESS, message: Optional[str] = None) -> None:
    """Safely exit the application with proper cleanup.

    Args:
        exit_code: Exit code to use
        message: Optional message to display before exiting
    """
    logger = logging.getLogger(__name__)

    if message:
        if exit_code == ExitCode.SUCCESS:
            console.success(message)
        else:
            console.error(message)

    logger.debug("Exiting with code: %d", exit_code)

    try:
        # Perform any final cleanup
        _cleanup_on_error(None)
    except Exception as e:
        logger.warning("Error during final cleanup: %s", e)

    sys.exit(exit_code)


# Context manager for error handling in specific code blocks
class ErrorHandler:
    """Context manager for handling errors in specific code blocks.

    This can be used within commands for more granular error handling
    of specific operations that might fail.

    Example:
        with ErrorHandler("Processing template", verbose=True):
            process_template(template_path)
    """

    def __init__(
        self,
        operation_name: str,
        verbose: bool = False,
        exit_on_error: bool = False,
        show_suggestions: bool = True,
    ) -> None:
        """Initialize the error handler.

        Args:
            operation_name: Name of the operation being performed
            verbose: Whether to show verbose error information
            exit_on_error: Whether to exit immediately on error
            show_suggestions: Whether to show helpful suggestions
        """
        self.operation_name = operation_name
        self.verbose = verbose
        self.exit_on_error = exit_on_error
        self.show_suggestions = show_suggestions
        self.logger = logging.getLogger(__name__)

    def __enter__(self) -> "ErrorHandler":
        """Enter the error handling context."""
        self.logger.debug("Starting operation: %s", self.operation_name)
        return self

    def __exit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[Any],
    ) -> bool:
        """Exit the error handling context.

        Args:
            exc_type: Exception type if an exception occurred
            exc_val: Exception value if an exception occurred
            exc_tb: Exception traceback if an exception occurred

        Returns:
            True if exception was handled, False to re-raise
        """
        if exc_type is None:
            # No exception, operation completed successfully
            self.logger.debug(
                "Operation completed successfully: %s", self.operation_name
            )
            return True

        if not isinstance(exc_val, Exception):
            # Not a regular exception, let it propagate
            return False

        # Log the error
        self.logger.error(
            "Operation failed: %s, exception: %s",
            self.operation_name,
            type(exc_val).__name__,
        )

        # Display error with context
        console.error(f"Failed to {self.operation_name.lower()}")
        display_error(
            exc_val, verbose=self.verbose, show_suggestions=self.show_suggestions
        )

        if self.exit_on_error:
            # Exit immediately with appropriate code
            exit_code = get_exit_code(exc_val)
            sys.exit(exit_code)

        # Exception was handled, don't re-raise
        return True


# Convenience functions for common error handling patterns
def handle_file_operation(
    operation: Callable[[], Any], operation_name: str, verbose: bool = False
) -> Any:
    """Handle file operations with proper error handling.

    Args:
        operation: Function to execute
        operation_name: Description of the operation
        verbose: Whether to show verbose error information

    Returns:
        Result of the operation

    Raises:
        FileSystemError: If the operation fails with appropriate context
    """
    with ErrorHandler(operation_name, verbose=verbose):
        try:
            return operation()
        except (OSError, IOError, PermissionError) as e:
            raise FileSystemError(
                f"Failed to {operation_name.lower()}: {e}",
                operation=operation_name,
                error_code="file_operation_failed",
            ) from e


def handle_configuration_load(
    loader: Callable[[], Any], config_path: str, verbose: bool = False
) -> Any:
    """Handle configuration loading with proper error handling.

    Args:
        loader: Function to load the configuration
        config_path: Path to the configuration file
        verbose: Whether to show verbose error information

    Returns:
        Loaded configuration

    Raises:
        ConfigurationError: If loading fails with appropriate context
    """
    with ErrorHandler(f"Loading configuration from {config_path}", verbose=verbose):
        try:
            return loader()
        except Exception as e:
            raise ConfigurationError(
                f"Failed to load configuration: {e}",
                config_path=config_path,
                error_code="config_load_failed",
            ) from e
