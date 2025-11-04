"""
Logging Configuration for ANSYS Automation Scripts
===================================================

Provides consistent logging functionality across all scripts.
"""
# pylint: disable=undefined-variable
# pyright: reportUndefinedVariable=false
# type: ignore

# Global logging setting
_LOG_ENABLED = True


def set_logging(enabled):
    """
    Enable or disable logging globally.

    Args:
        enabled (bool): True to enable logging, False to disable
    """
    global _LOG_ENABLED
    _LOG_ENABLED = enabled


def log(message, level="INFO"):
    """
    Log a message with optional severity level.

    Args:
        message (str): Message to log
        level (str): Severity level (INFO, WARNING, ERROR)
    """
    if _LOG_ENABLED:
        prefix = f"[{level}]" if level != "INFO" else ""
        print(f"{prefix} {message}".strip())


def log_separator(char="=", length=70):
    """
    Print a separator line for visual organization.

    Args:
        char (str): Character to use for separator
        length (int): Length of separator line
    """
    if _LOG_ENABLED:
        print(char * length)


def log_section(title):
    """
    Print a section header.

    Args:
        title (str): Section title
    """
    if _LOG_ENABLED:
        log_separator()
        log(title)
        log_separator()
