"""Custom exception hierarchy for AI Forge.

This module defines a comprehensive exception hierarchy for proper error handling
throughout the AI Forge CLI application.
"""

from typing import Any, Optional


class AIForgeError(Exception):
    """Base exception class for all AI Forge errors.

    This is the root exception that all other AI Forge exceptions inherit from.
    It provides standard error handling capabilities including error codes and
    exception chaining support.

    Attributes:
        message: Human-readable error message
        error_code: Optional error code for programmatic handling
        details: Optional additional error details
    """

    def __init__(
        self,
        message: str,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
        *args: Any,
    ) -> None:
        """Initialize AIForgeError.

        Args:
            message: Human-readable error message
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error context
            *args: Additional arguments passed to base Exception
        """
        super().__init__(message, *args)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def __str__(self) -> str:
        """Return string representation of the error."""
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message

    def __repr__(self) -> str:
        """Return detailed string representation for debugging."""
        return (
            f"{self.__class__.__name__}("
            f"message={self.message!r}, "
            f"error_code={self.error_code!r}, "
            f"details={self.details!r})"
        )


class ConfigurationError(AIForgeError):
    """Raised when there are configuration-related errors.

    This exception is used for errors in reading, parsing, or validating
    configuration files, settings, or parameters.

    Examples:
        - Invalid YAML/JSON syntax in config files
        - Missing required configuration parameters
        - Invalid configuration values
        - Configuration file not found
    """

    def __init__(
        self,
        message: str,
        config_path: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize ConfigurationError.

        Args:
            message: Human-readable error message
            config_path: Optional path to the problematic config file
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error context
        """
        super().__init__(message, error_code, details)
        self.config_path = config_path
        if config_path:
            self.details["config_path"] = config_path


class TemplateError(AIForgeError):
    """Raised when there are template-related errors.

    This exception is used for errors in template processing, rendering,
    validation, or file operations.

    Examples:
        - Template file not found
        - Invalid template syntax
        - Template rendering failures
        - Missing template variables
        - Template security violations
    """

    def __init__(
        self,
        message: str,
        template_name: Optional[str] = None,
        template_path: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize TemplateError.

        Args:
            message: Human-readable error message
            template_name: Optional name of the problematic template
            template_path: Optional path to the template file
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error context
        """
        super().__init__(message, error_code, details)
        self.template_name = template_name
        self.template_path = template_path
        if template_name:
            self.details["template_name"] = template_name
        if template_path:
            self.details["template_path"] = template_path


class TemplateSecurityError(TemplateError):
    """Raised when template security validation fails.

    This exception is used specifically for security-related template errors,
    such as path traversal attempts or dangerous content detection.

    Examples:
        - Path traversal attempts in template paths
        - Dangerous code patterns in template content
        - Unauthorized file access attempts
        - Malicious template variables
    """

    pass


class TemplateValidationError(TemplateError):
    """Raised when template validation fails.

    This exception is used for structural validation errors in templates,
    such as missing required files or invalid manifest data.

    Examples:
        - Missing template.yaml manifest
        - Invalid manifest structure
        - Missing required template files
        - Circular template dependencies
    """

    pass


class TemplateRenderError(TemplateError):
    """Raised when template rendering fails.

    This exception is used for errors that occur during the template
    rendering process, such as missing variables or Jinja2 syntax errors.

    Examples:
        - Missing required template variables
        - Jinja2 syntax errors
        - Template file read errors during rendering
        - Output directory creation failures
    """

    pass


class ValidationError(AIForgeError):
    """Raised when validation of user input or data fails.

    This exception is used for errors in validating user inputs, command
    arguments, file contents, or any other data validation operations.

    Examples:
        - Invalid command line arguments
        - File content validation failures
        - Schema validation errors
        - Security validation failures
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        invalid_value: Optional[Any] = None,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize ValidationError.

        Args:
            message: Human-readable error message
            field_name: Optional name of the field that failed validation
            invalid_value: Optional value that failed validation
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error context
        """
        super().__init__(message, error_code, details)
        self.field_name = field_name
        self.invalid_value = invalid_value
        if field_name:
            self.details["field_name"] = field_name
        if invalid_value is not None:
            self.details["invalid_value"] = str(invalid_value)


class FileSystemError(AIForgeError):
    """Raised when file system operations fail.

    This exception is used for errors in file and directory operations,
    including permission errors, path issues, and I/O failures.

    Examples:
        - File or directory not found
        - Permission denied errors
        - Disk space issues
        - Path traversal security violations
        - File creation/deletion failures
    """

    def __init__(
        self,
        message: str,
        path: Optional[str] = None,
        operation: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize FileSystemError.

        Args:
            message: Human-readable error message
            path: Optional file system path that caused the error
            operation: Optional description of the failed operation
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error context
        """
        super().__init__(message, error_code, details)
        self.path = path
        self.operation = operation
        if path:
            self.details["path"] = path
        if operation:
            self.details["operation"] = operation


class DependencyError(AIForgeError):
    """Raised when there are dependency-related errors.

    This exception is used for errors related to missing dependencies,
    version conflicts, or dependency resolution failures.

    Examples:
        - Missing required packages
        - Version compatibility issues
        - Package installation failures
        - Import errors for required modules
    """

    def __init__(
        self,
        message: str,
        dependency_name: Optional[str] = None,
        required_version: Optional[str] = None,
        found_version: Optional[str] = None,
        error_code: Optional[str] = None,
        details: Optional[dict[str, Any]] = None,
    ) -> None:
        """Initialize DependencyError.

        Args:
            message: Human-readable error message
            dependency_name: Optional name of the problematic dependency
            required_version: Optional required version specification
            found_version: Optional version that was found (if any)
            error_code: Optional error code for programmatic handling
            details: Optional dictionary with additional error context
        """
        super().__init__(message, error_code, details)
        self.dependency_name = dependency_name
        self.required_version = required_version
        self.found_version = found_version
        if dependency_name:
            self.details["dependency_name"] = dependency_name
        if required_version:
            self.details["required_version"] = required_version
        if found_version:
            self.details["found_version"] = found_version


# Convenience function for exception chaining
def chain_exception(
    new_exception: AIForgeError,
    original_exception: Exception,
    context: Optional[str] = None,
) -> AIForgeError:
    """Chain exceptions to preserve error context.

    This function helps maintain the full error chain when converting
    from built-in exceptions to AI Forge exceptions.

    Args:
        new_exception: The new AI Forge exception to raise
        original_exception: The original exception that was caught
        context: Optional additional context about where the chaining occurred

    Returns:
        The new exception with proper chaining set up

    Example:
        try:
            risky_operation()
        except ValueError as e:
            raise chain_exception(
                ValidationError("Invalid input provided"),
                e,
                "during user input validation"
            )
    """
    # Set the original exception as the cause
    new_exception.__cause__ = original_exception

    # Add chaining context to details
    if context:
        new_exception.details["chain_context"] = context

    # Add original exception info to details
    new_exception.details["original_exception"] = {
        "type": type(original_exception).__name__,
        "message": str(original_exception),
    }

    return new_exception
