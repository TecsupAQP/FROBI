"""M14 · Asistente: contract with the front. The live part is the WebSocket (see router)."""

from typing import Literal

from pydantic import BaseModel, Field

from frobi.modules.assistant.application import ConversationView
from frobi.modules.assistant.domain import MAX_QUESTIONS


class ChatLineOut(BaseModel):
    speaker: Literal["person", "assistant"]
    text: str


class ConversationOut(BaseModel):
    enabled: bool = Field(description="Hay IA configurada; si no, responde con ayuda fija.")
    lines: list[ChatLineOut] = Field(description="La conversación, la más antigua primero.")
    questions_left: int = Field(description=f"Preguntas que quedan (de {MAX_QUESTIONS}).")
    answering: bool = Field(description="Está respondiendo una pregunta en este momento.")

    @classmethod
    def from_view(cls, view: ConversationView, *, enabled: bool) -> "ConversationOut":
        return cls(
            enabled=enabled,
            lines=[ChatLineOut(speaker=line.speaker.value, text=line.text) for line in view.lines],
            questions_left=view.questions_left,
            answering=view.answering,
        )
