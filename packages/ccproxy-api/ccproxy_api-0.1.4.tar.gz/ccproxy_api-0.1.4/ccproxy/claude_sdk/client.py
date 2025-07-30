"""Claude SDK client wrapper for handling core Claude Code SDK interactions."""

from collections.abc import AsyncIterator
from typing import Any

import structlog
from pydantic import BaseModel

from ccproxy.core.async_utils import patched_typing
from ccproxy.core.errors import ClaudeProxyError, ServiceUnavailableError
from ccproxy.models import claude_sdk as sdk_models
from ccproxy.observability import timed_operation


with patched_typing():
    from claude_code_sdk import (
        AssistantMessage as SDKAssistantMessage,
    )
    from claude_code_sdk import (
        ClaudeCodeOptions,
        CLIConnectionError,
        CLIJSONDecodeError,
        CLINotFoundError,
        ProcessError,
        query,
    )
    from claude_code_sdk import (
        ResultMessage as SDKResultMessage,
    )
    from claude_code_sdk import (
        SystemMessage as SDKSystemMessage,
    )
    from claude_code_sdk import (
        UserMessage as SDKUserMessage,
    )


logger = structlog.get_logger(__name__)


class ClaudeSDKError(Exception):
    """Base exception for Claude SDK errors."""


class ClaudeSDKConnectionError(ClaudeSDKError):
    """Raised when unable to connect to Claude Code."""


class ClaudeSDKProcessError(ClaudeSDKError):
    """Raised when Claude Code process fails."""


class ClaudeSDKClient:
    """
    Minimal Claude SDK client wrapper that handles core SDK interactions.

    This class provides a clean interface to the Claude Code SDK while handling
    error translation and basic query execution.
    """

    def __init__(self) -> None:
        """Initialize the Claude SDK client."""
        self._last_api_call_time_ms: float = 0.0

    async def query_completion(
        self, prompt: str, options: ClaudeCodeOptions, request_id: str | None = None
    ) -> AsyncIterator[
        sdk_models.UserMessage
        | sdk_models.AssistantMessage
        | sdk_models.SystemMessage
        | sdk_models.ResultMessage
    ]:
        """
        Execute a query using the Claude Code SDK and yields strongly-typed Pydantic models.

        Args:
            prompt: The prompt string to send to Claude
            options: Claude Code options configuration
            request_id: Optional request ID for correlation

        Yields:
            Strongly-typed Pydantic messages from ccproxy.claude_sdk.models

        Raises:
            ClaudeSDKError: If the query fails
        """
        async with timed_operation("claude_sdk_query", request_id) as op:
            try:
                logger.debug("claude_sdk_query_start", prompt_length=len(prompt))

                message_count = 0
                async for message in query(prompt=prompt, options=options):
                    message_count += 1

                    logger.debug(
                        "claude_sdk_raw_message_received",
                        message_type=type(message).__name__,
                        message_count=message_count,
                        request_id=request_id,
                        has_content=hasattr(message, "content")
                        and bool(getattr(message, "content", None)),
                        content_preview=str(message)[:150],
                    )

                    model_class: type[BaseModel] | None = None
                    if isinstance(message, SDKUserMessage):
                        model_class = sdk_models.UserMessage
                    elif isinstance(message, SDKAssistantMessage):
                        model_class = sdk_models.AssistantMessage
                    elif isinstance(message, SDKSystemMessage):
                        model_class = sdk_models.SystemMessage
                    elif isinstance(message, SDKResultMessage):
                        model_class = sdk_models.ResultMessage

                    # Convert Claude SDK message to our Pydantic model
                    try:
                        if hasattr(message, "__dict__"):
                            converted_message = model_class.model_validate(
                                vars(message)
                            )
                        else:
                            # For dataclass objects, use dataclass.asdict equivalent
                            message_dict = {}
                            if hasattr(message, "__dataclass_fields__"):
                                message_dict = {
                                    field: getattr(message, field)
                                    for field in message.__dataclass_fields__
                                }
                            else:
                                # Try to extract common attributes
                                for attr in [
                                    "content",
                                    "subtype",
                                    "data",
                                    "session_id",
                                    "stop_reason",
                                    "usage",
                                    "total_cost_usd",
                                ]:
                                    if hasattr(message, attr):
                                        message_dict[attr] = getattr(message, attr)

                            converted_message = model_class.model_validate(message_dict)

                        logger.debug(
                            "claude_sdk_message_converted_successfully",
                            original_type=type(message).__name__,
                            converted_type=type(converted_message).__name__,
                            message_count=message_count,
                            request_id=request_id,
                        )
                        yield converted_message
                    except Exception as e:
                        logger.warning(
                            "claude_sdk_message_conversion_failed",
                            message_type=type(message).__name__,
                            model_class=model_class.__name__,
                            error=str(e),
                        )
                        # Skip invalid messages rather than crashing
                        continue

                # Store final metrics
                op["message_count"] = message_count
                self._last_api_call_time_ms = op.get("duration_ms", 0.0)

                logger.debug(
                    "claude_sdk_query_completed",
                    message_count=message_count,
                    duration_ms=op.get("duration_ms"),
                )

            except (CLINotFoundError, CLIConnectionError) as e:
                logger.error(
                    "claude_sdk_connection_failed",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise ServiceUnavailableError(
                    f"Claude CLI not available: {str(e)}"
                ) from e
            except (ProcessError, CLIJSONDecodeError) as e:
                logger.error(
                    "claude_sdk_process_failed",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise ClaudeProxyError(
                    message=f"Claude process error: {str(e)}",
                    error_type="service_unavailable_error",
                    status_code=503,
                ) from e
            except Exception as e:
                logger.error(
                    "claude_sdk_unexpected_error_occurred",
                    error=str(e),
                    error_type=type(e).__name__,
                )
                raise ClaudeProxyError(
                    message=f"Unexpected error: {str(e)}",
                    error_type="internal_server_error",
                    status_code=500,
                ) from e

    def get_last_api_call_time_ms(self) -> float:
        """
        Get the duration of the last Claude API call in milliseconds.

        Returns:
            Duration in milliseconds, or 0.0 if no call has been made yet
        """
        return self._last_api_call_time_ms

    async def validate_health(self) -> bool:
        """
        Validate that the Claude SDK is healthy.

        Returns:
            True if healthy, False otherwise
        """
        try:
            logger.debug("health_check_start", component="claude_sdk")

            # Simple health check - the SDK is available if we can import it
            # More sophisticated checks could be added here
            is_healthy = True

            logger.debug(
                "health_check_completed", component="claude_sdk", healthy=is_healthy
            )
            return is_healthy
        except Exception as e:
            logger.error(
                "health_check_failed",
                component="claude_sdk",
                error=str(e),
                error_type=type(e).__name__,
            )
            return False

    async def close(self) -> None:
        """Close the client and cleanup resources."""
        # Claude Code SDK doesn't require explicit cleanup
        pass

    async def __aenter__(self) -> "ClaudeSDKClient":
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit."""
        await self.close()
