"""M14 · Asistente: a private chat with FROBI, over a WebSocket.

``WS /api/v1/assistant/ws`` (JSON messages):

- Client → server: ``{"type": "auth", "token": "…"}`` first (within 10 s), then
  ``{"type": "ask", "question": "…", "material_id": "…" | null}`` or ``{"type": "ping"}``.
- Server → client: ``ready``; ``question`` (text), ``tool`` (status), ``text`` (a piece of the
  answer), ``done`` (fallback, questions_left); ``restarted``; ``error`` (code, message); ``pong``.

Every event of a person's answer goes to all of that person's open sockets, on any instance
(Redis pub/sub), so two tabs or two devices stay in sync.
"""

import asyncio
import contextlib
import logging
from typing import Annotated, Any, cast
from uuid import UUID

from fastapi import APIRouter, Depends, Response, WebSocket, WebSocketDisconnect, status

from frobi.modules.assistant.application import (
    AnswerEvent,
    AskCommand,
    ConversationHandler,
    Finished,
)
from frobi.modules.assistant.application.ports import TextChunk, ToolUsed
from frobi.modules.assistant.infrastructure import RedisHub, assistant_enabled
from frobi.shared.application import TokenResolver
from frobi.shared.domain import DomainError
from frobi.shared.infrastructure import Settings
from frobi.shared.presentation import AUTH_RESPONSES, CurrentPersonId, get_settings, problem

from .dependencies import ask_handler, get_conversation_handler, get_hub
from .schemas import ConversationOut

AUTH_TIMEOUT_SECONDS = 10
# WebSocket close codes in the application range (4000-4999).
CLOSE_UNAUTHENTICATED = 4401
UNEXPECTED = "No pude recibir tu pregunta. Inténtalo de nuevo en un momento."

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/assistant", tags=["M14 · Asistente"], responses=AUTH_RESPONSES)

# Answers keep running if the socket that asked closes: other tabs still get them, and the
# conversation is saved. Strong references so the event loop does not drop them.
_answers: set[asyncio.Task[None]] = set()


@router.get("/conversation", summary="Mi conversación con el asistente")
async def get_conversation(
    person_id: CurrentPersonId,
    handler: Annotated[ConversationHandler, Depends(get_conversation_handler)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> ConversationOut:
    view = await handler.read(person_id)
    return ConversationOut.from_view(view, enabled=assistant_enabled(settings))


@router.delete(
    "/conversation",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Empezar una conversación nueva",
    responses={409: problem("Todavía está respondiendo (`Assistant.StillAnswering`).")},
)
async def restart_conversation(
    person_id: CurrentPersonId,
    handler: Annotated[ConversationHandler, Depends(get_conversation_handler)],
    hub: Annotated[RedisHub, Depends(get_hub)],
) -> Response:
    await handler.restart(person_id)
    await hub.publish(person_id, {"type": "restarted"})
    return Response(status_code=status.HTTP_204_NO_CONTENT)


def _wire(event: AnswerEvent) -> dict[str, Any]:
    if isinstance(event, TextChunk):
        return {"type": "text", "text": event.text}
    if isinstance(event, ToolUsed):
        return {"type": "tool", "status": event.status}
    if isinstance(event, Finished):
        return {"type": "done", "fallback": event.fallback, "questions_left": event.questions_left}
    raise TypeError(event)


def _error(error: DomainError) -> dict[str, Any]:
    return {"type": "error", "code": error.code, "message": error.message}


async def _authenticate(websocket: WebSocket) -> UUID | None:
    try:
        message = await asyncio.wait_for(websocket.receive_json(), AUTH_TIMEOUT_SECONDS)
    except (TimeoutError, ValueError, WebSocketDisconnect):
        return None
    token = message.get("token") if isinstance(message, dict) else None
    if message.get("type") != "auth" or not isinstance(token, str) or not token.strip():
        return None
    resolver = cast(TokenResolver, websocket.app.state.token_resolver)
    return await resolver.resolve(token.strip())


async def _answer(
    websocket: WebSocket, person_id: UUID, message: dict[str, Any], own: asyncio.Queue[Any]
) -> None:
    """Runs one question. Errors before the answer starts go only to the socket that asked."""
    state = websocket.app.state
    hub = cast(RedisHub, state.assistant_hub)
    raw_guide = message.get("material_id")
    try:
        open_guide = UUID(raw_guide) if isinstance(raw_guide, str) and raw_guide else None
    except ValueError:
        open_guide = None
    question = message.get("question")
    async with state.session_factory() as session:
        handler = ask_handler(state, session)
        try:
            prepared = await handler.prepare(
                AskCommand(
                    person_id=person_id,
                    question=question if isinstance(question, str) else "",
                    open_guide=open_guide,
                )
            )
        except DomainError as error:
            own.put_nowait(_error(error))
            return
        except Exception:
            logger.exception("Assistant question could not start")
            own.put_nowait(
                {"type": "error", "code": "Assistant.Unavailable", "message": UNEXPECTED}
            )
            return
        await hub.publish(person_id, {"type": "question", "text": prepared.text})
        async for event in handler.answer(prepared):
            await hub.publish(person_id, _wire(event))


async def _send_all(websocket: WebSocket, *queues: asyncio.Queue[Any]) -> None:
    """The only writer of the socket: hub events and this socket's own replies."""
    waiting = {asyncio.ensure_future(q.get()): q for q in queues}
    try:
        while True:
            done, _ = await asyncio.wait(waiting, return_when=asyncio.FIRST_COMPLETED)
            for future in done:
                queue = waiting.pop(future)
                await websocket.send_json(future.result())
                waiting[asyncio.ensure_future(queue.get())] = queue
    finally:
        for future in waiting:
            future.cancel()


@router.websocket("/ws")
async def assistant_socket(websocket: WebSocket) -> None:
    await websocket.accept()
    person_id = await _authenticate(websocket)
    if person_id is None:
        await websocket.close(code=CLOSE_UNAUTHENTICATED, reason="Sin sesión")
        return
    hub = cast(RedisHub, websocket.app.state.assistant_hub)
    own: asyncio.Queue[Any] = asyncio.Queue()
    async with hub.listen(person_id) as events:
        own.put_nowait({"type": "ready"})
        sender = asyncio.create_task(_send_all(websocket, own, events))
        try:
            while True:
                message = await websocket.receive_json()
                kind = message.get("type") if isinstance(message, dict) else None
                if kind == "ask":
                    task = asyncio.create_task(_answer(websocket, person_id, message, own))
                    _answers.add(task)
                    task.add_done_callback(_finished)
                elif kind == "ping":
                    own.put_nowait({"type": "pong"})
        except (WebSocketDisconnect, ValueError):
            pass
        finally:
            sender.cancel()
            with contextlib.suppress(asyncio.CancelledError, Exception):
                await sender


def _finished(task: "asyncio.Task[None]") -> None:
    _answers.discard(task)
    if not task.cancelled() and task.exception() is not None:
        logger.error("Assistant answer failed", exc_info=task.exception())
