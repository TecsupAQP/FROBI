"""Close the current session: the token stops working right away."""

from frobi.modules.identity.application.ports import SessionStore


class EndSessionHandler:
    def __init__(self, sessions: SessionStore) -> None:
        self._sessions = sessions

    async def handle(self, token: str) -> None:
        await self._sessions.revoke(token)
