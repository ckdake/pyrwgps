"""Rate limiting utilities for the ridewithgps package."""

import time
from threading import Lock
from typing import Optional


class RateExceededError(Exception):
    """Exception raised when the rate limit is exceeded."""


class RateLimiter:
    """A simple thread-safe rate limiter."""

    # pylint: disable=too-few-public-methods

    def __init__(self, max_messages: int = 10, every_seconds: int = 1):
        """
        Initialize the rate limiter.

        Args:
            max_messages: Maximum number of messages allowed per window.
            every_seconds: Length of the rate window in seconds.
        """
        self.max_messages = max_messages
        self.every_seconds = every_seconds
        self.lock = Lock()
        self._reset_window()

    def _reset_window(self):
        """Reset the rate window."""
        self.window_num = 0
        self.window_time = time.time()

    def acquire(self, block: bool = True, timeout: Optional[float] = None):
        """
        Acquire permission to proceed, enforcing the rate limit.

        Args:
            block: If False, raise immediately if rate limit is exceeded.
            timeout: Maximum time to wait for a slot.

        Raises:
            RateExceededError: If the rate limit is exceeded and block is False or timeout reached.
        """
        with self.lock:
            now = time.time()
            if now - self.window_time > self.every_seconds:
                # New rate window
                self._reset_window()

            if self.window_num >= self.max_messages:
                # Rate exceeding
                if not block:
                    raise RateExceededError()

                wait_time = self.window_time + self.every_seconds - now
                if timeout and wait_time > timeout:
                    time.sleep(timeout)
                    raise RateExceededError()

                # Release lock while sleeping, then reacquire using 'with'
                self.lock.release()
                try:
                    time.sleep(wait_time)
                finally:
                    # pylint: disable=consider-using-with
                    self.lock.acquire()
                self._reset_window()

            self.window_num += 1
