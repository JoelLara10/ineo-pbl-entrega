from collections import defaultdict, deque
from threading import Lock
from time import time


class LoginAttemptLimiter:
    """Límite temporal de intentos por usuario e IP, sin guardar contraseñas."""

    def __init__(self):
        self._attempts = defaultdict(deque)
        self._lock = Lock()

    @staticmethod
    def key(username, remote_addr):
        return f"{(remote_addr or 'unknown').strip()}:{username.casefold()}"

    def _purge(self, attempts, now, window_seconds):
        while attempts and attempts[0] <= now - window_seconds:
            attempts.popleft()

    def check(self, key, max_attempts, window_seconds, now=None):
        now = time() if now is None else now
        with self._lock:
            attempts = self._attempts[key]
            self._purge(attempts, now, window_seconds)
            if len(attempts) < max_attempts:
                return True, 0
            retry_after = max(1, int(window_seconds - (now - attempts[0])))
            return False, retry_after

    def failure(self, key, window_seconds, now=None):
        now = time() if now is None else now
        with self._lock:
            attempts = self._attempts[key]
            self._purge(attempts, now, window_seconds)
            attempts.append(now)

    def success(self, key):
        with self._lock:
            self._attempts.pop(key, None)

    def reset(self):
        with self._lock:
            self._attempts.clear()


login_limiter = LoginAttemptLimiter()
