"""One HTTP session per provider instance, so its searches reuse a connection."""

from typing import Self

import anyenv


class HttpSessionMixin:
    """Gives a provider one `anyenv.HttpSession`, opened on first use.

    A session's client belongs to the event loop it was opened on: on another loop
    (e.g. each `anyenv.run_sync` call) a new one is opened. Close it with `aclose()`
    or use the provider as `async with provider: ...` (else garbage collection
    drops its connections).
    """

    _http_session: anyenv.HttpSession | None = None

    async def _session(self) -> anyenv.HttpSession:
        session = self._http_session
        if session is None or not session.usable_here():
            session = anyenv.HttpSession()
            # Binds it to this loop; doesn't suspend, so concurrent first calls share it.
            await session.__aenter__()
            self._http_session = session
        return session

    async def aclose(self) -> None:
        """Close the HTTP session (its connections)."""
        session, self._http_session = self._http_session, None
        if session is not None and session.usable_here():
            await session.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await self.aclose()
