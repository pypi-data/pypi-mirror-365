"""
Analytics module for tracking CLI usage with PostHog
"""

import hashlib
import logging
import os
import platform
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

try:
    from posthog import Posthog
    POSTHOG_AVAILABLE = True
except ImportError:
    POSTHOG_AVAILABLE = False
    logger.warning("PostHog not available. Analytics disabled.")


API_KEY = "phc_7M8xhUTqBRGMlEytOcDzPw20YMHEY05vKoSjqMnBAPO"

class Analytics:
    """Analytics client for tracking CLI usage"""

    def __init__(self, enabled: bool = True):
        self.enabled = enabled and POSTHOG_AVAILABLE
        self.anonymous_id = self._get_or_create_user_id()
        self.user_id = self.anonymous_id  # Start with anonymous ID
        self.is_identified = False
        self.posthog = None

        if self.enabled:
            # Initialize Posthog with API key and host
            try:
                self.posthog = Posthog(API_KEY, host='https://us.i.posthog.com')
                # Test the connection by making a simple call
                self.posthog.capture(
                    distinct_id="test",
                    event="test_connection",
                    properties={"test": True}
                )
                logger.debug(f"Analytics initialized for user: {self.user_id}")
            except Exception as e:
                logger.debug(f"Failed to initialize PostHog: {e}")
                self.enabled = False
        else:
            logger.debug("Analytics disabled or PostHog not available")

    def _get_or_create_user_id(self) -> str:
        """Get or create anonymous user ID based on machine characteristics"""
        # Create a unique but anonymous identifier based on machine info
        machine_info = f"{platform.machine()}-{platform.system()}-{platform.node()}"
        user_id = hashlib.sha256(machine_info.encode()).hexdigest()[:16]
        return f"cli_user_{user_id}"

    def _get_system_properties(self) -> Dict[str, Any]:
        """Get system information for analytics"""
        return {
            "os": platform.system(),
            "os_version": platform.version(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "machine": platform.machine(),
        }

    def track(self, event: str, properties: Optional[Dict[str, Any]] = None):
        """Track an event"""
        if not self.enabled:
            return

        try:
            all_properties = self._get_system_properties()
            if properties:
                all_properties.update(properties)

            self.posthog.capture(
                distinct_id=self.user_id,
                event=event,
                properties=all_properties
            )
            logger.debug(f"Tracked event: {event}")
        except Exception as e:
            logger.debug(f"Failed to track event {event}: {e}")

    def track_cli_start(self, command: str, mode: str, args: Dict[str, Any]):
        """Track CLI command start"""
        properties = {
            "command": command,
            "mode": mode,
            "args": args,
        }
        self.track("cli_command_started", properties)

    def track_cli_complete(self, command: str, mode: str, processed_count: int,
                          failed_count: int, duration_seconds: float):
        """Track CLI command completion"""
        properties = {
            "command": command,
            "mode": mode,
            "processed_count": processed_count,
            "failed_count": failed_count,
            "duration_seconds": duration_seconds,
            "success_rate": processed_count / (processed_count + failed_count) if (processed_count + failed_count) > 0 else 0
        }
        self.track("cli_command_completed", properties)

    def track_error(self, error_type: str, error_message: str, command: str = None):
        """Track errors"""
        properties = {
            "error_type": error_type,
            "error_message": error_message[:200],  # Truncate long messages
            "command": command,
        }
        self.track("cli_error", properties)

    def track_browser_automation(self, action: str, success: bool, error: str = None):
        """Track browser automation events"""
        properties = {
            "action": action,
            "success": success,
            "error": error[:200] if error else None,
        }
        self.track("browser_automation", properties)

    def identify_user(self, user_id: str, properties: Optional[Dict[str, Any]] = None):
        """Identify a user with PostHog and link with anonymous ID"""
        if not self.enabled or self.is_identified:
            return

        try:
            # First, alias the anonymous user to the authenticated user ID
            # This links all previous anonymous events to the authenticated user
            self.posthog.alias(
                distinct_id=user_id,
                alias=self.anonymous_id
            )

            # Update our internal user ID
            self.user_id = user_id
            self.is_identified = True

            # Identify the user in PostHog with their properties
            user_properties = self._get_system_properties()
            if properties:
                user_properties.update(properties)

            self.posthog.identify(
                distinct_id=user_id,
                properties=user_properties
            )
            logger.debug(f"Identified and aliased user: {user_id} (was {self.anonymous_id})")
        except Exception as e:
            logger.debug(f"Failed to identify user: {e}")

    def flush(self):
        """Flush pending events"""
        if self.enabled:
            try:
                self.posthog.flush()
            except Exception as e:
                logger.debug(f"Failed to flush analytics: {e}")


# Global analytics instance
_analytics_instance: Optional[Analytics] = None


def get_analytics(enabled: bool = True) -> Analytics:
    """Get the global analytics instance"""
    global _analytics_instance
    if _analytics_instance is None:
        # Check if analytics is disabled via environment variable
        analytics_disabled = os.getenv("POPSY_DISABLE_ANALYTICS", "false").lower() in ("true", "1", "yes")
        _analytics_instance = Analytics(enabled=enabled and not analytics_disabled)
    return _analytics_instance


def track_event(event: str, properties: Optional[Dict[str, Any]] = None):
    """Convenience function to track events"""
    analytics = get_analytics()
    analytics.track(event, properties)
