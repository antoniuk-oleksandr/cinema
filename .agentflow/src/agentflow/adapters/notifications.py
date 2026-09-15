import asyncio
import logging
import shutil

log = logging.getLogger(__name__)

class NotificationService:
    async def _notify(self, title, body) -> None:
        try:
            if shutil.which("notify-send"):
                await asyncio.create_subprocess_exec("notify-send", title, body)
        except (OSError, TimeoutError) as exc:
            log.warning("desktop notification failed: %s", exc)

    async def success(self, body) -> None:
        await self._notify("Agentflow complete", body)

    async def attention(self, body) -> None:
        await self._notify("Agentflow needs attention", body)

    async def failure(self, body) -> None:
        await self._notify("Agentflow failed", body)
