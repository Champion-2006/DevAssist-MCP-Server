"""
Custom exception hierarchy for DevAssist MCP Server.

Provides structured exceptions for different error categories
with status codes and detailed error information.
"""


class DevAssistError(Exception):
    """Base exception for all DevAssist MCP errors."""

    def __init__(
        self,
        message: str = "An unexpected error occurred",
        status_code: int = 500,
        details: dict | None = None,
    ) -> None:
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> dict:
        """Convert exception to a dictionary for JSON serialization."""
        return {
            "error": self.__class__.__name__,
            "message": self.message,
            "status_code": self.status_code,
            "details": self.details,
        }


class ExternalAPIError(DevAssistError):
    """Exception raised when an external API call fails."""

    def __init__(
        self,
        message: str = "External API request failed",
        status_code: int = 502,
        details: dict | None = None,
        api_name: str = "Unknown",
    ) -> None:
        self.api_name = api_name
        super().__init__(
            message=f"[{api_name}] {message}",
            status_code=status_code,
            details=details,
        )


class GitHubAPIError(ExternalAPIError):
    """Exception raised when a GitHub API call fails."""

    def __init__(
        self,
        message: str = "GitHub API request failed",
        status_code: int = 502,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status_code,
            details=details,
            api_name="GitHub",
        )


class CodeforcesAPIError(ExternalAPIError):
    """Exception raised when a Codeforces API call fails."""

    def __init__(
        self,
        message: str = "Codeforces API request failed",
        status_code: int = 502,
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=status_code,
            details=details,
            api_name="Codeforces",
        )


class ValidationError(DevAssistError):
    """Exception raised when input validation fails."""

    def __init__(
        self,
        message: str = "Validation error",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=422,
            details=details,
        )


class ConfigurationError(DevAssistError):
    """Exception raised when configuration is invalid or missing."""

    def __init__(
        self,
        message: str = "Configuration error",
        details: dict | None = None,
    ) -> None:
        super().__init__(
            message=message,
            status_code=500,
            details=details,
        )
