"""Rate limiter en memoria (ventana deslizante simple) para endpoints de auth/2FA.

Para despliegues multi-instancia, sustituir por un backend Redis con la misma
interfaz `check(key)`. Aquí basta para un solo proceso / desarrollo.
"""
import time
from collections import defaultdict, deque

from app.core.config import settings


class RateLimiter:
    def __init__(self, limit: int, window: int) -> None:
        self.limit = limit
        self.window = window
        self._hits: dict[str, deque[float]] = defaultdict(deque)

    def check(self, key: str) -> tuple[bool, int]:
        """Devuelve (permitido, retry_after_segundos)."""
        now = time.time()
        q = self._hits[key]
        while q and now - q[0] > self.window:
            q.popleft()
        if len(q) >= self.limit:
            retry_after = int(self.window - (now - q[0])) + 1
            return False, retry_after
        q.append(now)
        return True, 0


auth_limiter = RateLimiter(settings.AUTH_RATE_LIMIT, settings.AUTH_RATE_WINDOW_SECONDS)
