"""Delivers assistant events to every open socket of a person, whatever instance it is on.

Each API instance keeps **one** Redis pub/sub connection. It subscribes to
``assistant:person:{person_id}`` while at least one of that person's sockets is connected to
this instance, and hands each message to those sockets' queues. Publishing goes through Redis,
so an answer produced on instance A reaches a tab connected to instance B.
"""

import asyncio
import contextlib
import json
import logging
from collections.abc import AsyncIterator
from typing import TYPE_CHECKING, Any
from uuid import UUID

if TYPE_CHECKING:
    from redis.asyncio import Redis
    from redis.asyncio.client import PubSub

logger = logging.getLogger(__name__)

# Keeps the pub/sub connection subscribed (and readable) while no person is connected.
CONTROL_CHANNEL = "assistant:hub"
QUEUE_SIZE = 1024
READ_TIMEOUT_SECONDS = 1.0


def person_channel(person_id: UUID) -> str:
    return f"assistant:person:{person_id}"


class RedisHub:
    def __init__(self, redis: "Redis") -> None:
        self._redis = redis
        self._pubsub: PubSub | None = None
        self._reader: asyncio.Task[None] | None = None
        self._listeners: dict[str, set[asyncio.Queue[dict[str, Any]]]] = {}
        self._lock = asyncio.Lock()

    async def publish(self, person_id: UUID, event: dict[str, Any]) -> None:
        await self._redis.publish(person_channel(person_id), json.dumps(event))

    @contextlib.asynccontextmanager
    async def listen(self, person_id: UUID) -> AsyncIterator["asyncio.Queue[dict[str, Any]]"]:
        """A queue with every event published for this person while the block is open."""
        channel = person_channel(person_id)
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(QUEUE_SIZE)
        async with self._lock:
            pubsub = await self._ensure_started()
            if channel not in self._listeners:
                self._listeners[channel] = set()
                await pubsub.subscribe(channel)
            self._listeners[channel].add(queue)
        try:
            yield queue
        finally:
            async with self._lock:
                listeners = self._listeners.get(channel, set())
                listeners.discard(queue)
                if not listeners and channel in self._listeners:
                    del self._listeners[channel]
                    if self._pubsub is not None:
                        await self._pubsub.unsubscribe(channel)

    async def close(self) -> None:
        if self._reader is not None:
            self._reader.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self._reader
            self._reader = None
        if self._pubsub is not None:
            await self._pubsub.aclose()  # type: ignore[no-untyped-call]
            self._pubsub = None

    async def _ensure_started(self) -> "PubSub":
        if self._pubsub is None:
            self._pubsub = self._redis.pubsub(ignore_subscribe_messages=True)
            await self._pubsub.subscribe(CONTROL_CHANNEL)
            self._reader = asyncio.create_task(self._read_forever(self._pubsub))
        return self._pubsub

    async def _read_forever(self, pubsub: "PubSub") -> None:
        while True:
            try:
                message = await pubsub.get_message(timeout=READ_TIMEOUT_SECONDS)
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.warning("Assistant hub lost Redis; retrying", exc_info=True)
                await asyncio.sleep(READ_TIMEOUT_SECONDS)
                continue
            if message is None or message.get("type") != "message":
                continue
            channel = message["channel"]
            channel = channel.decode() if isinstance(channel, bytes) else channel
            event = json.loads(message["data"])
            for queue in tuple(self._listeners.get(channel, ())):
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    # A socket that stopped reading must not hold up everyone else.
                    logger.warning("Dropping assistant event for a slow socket on %s", channel)
