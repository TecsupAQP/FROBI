"""The assistant on Claude (Anthropic SDK): a streaming tool-use loop.

Each request resends the conversation exactly as the API returned it (thinking and tool blocks
included) and only ever appends to it. Text is streamed to the person as it is generated; tool
calls run here, bound to the person asking (see ``application.tools``).
"""

import json
import logging
from collections.abc import AsyncIterator, Sequence
from typing import Any, Literal

import anthropic

from frobi.modules.assistant.application.ports import (
    Answered,
    AssistantEvent,
    AssistantTool,
    AssistantUnavailable,
    JsonObject,
    PersonContext,
    TextChunk,
    ToolFailed,
    ToolUsed,
)

from .system_prompt import GUIDE, person_context

DEFAULT_MODEL = "claude-opus-5-5"
MAX_TOKENS = 64_000
# Tool rounds in one answer before giving up (a normal answer needs one to three).
MAX_STEPS = 8
# Consecutive tool inputs the SDK could not parse at all before giving up on the answer.
MAX_JSON_RETRIES = 2
FALLBACK_BETA = "server-side-fallback-2026-07-01"
TIMEOUT_SECONDS = 120.0

Effort = Literal["low", "medium", "high", "xhigh", "max"]

logger = logging.getLogger(__name__)


def _tool_param(tool: AssistantTool) -> dict[str, Any]:
    return {
        "name": tool.name,
        "description": tool.description,
        "input_schema": tool.input_schema,
        "eager_input_streaming": True,
    }


async def _run(tool: AssistantTool | None, block: Any) -> dict[str, Any]:
    result: dict[str, Any] = {"type": "tool_result", "tool_use_id": block.id}
    if tool is None:
        return {**result, "is_error": True, "content": f"Unknown tool {block.name}."}
    arguments = block.input
    if not isinstance(arguments, dict) or any(
        isinstance(value, bool) or not isinstance(value, str | int) for value in arguments.values()
    ):
        # Eager input streaming skips server-side validation: check the shape here.
        return {**result, "is_error": True, "content": json.dumps({"INVALID_JSON": arguments})}
    try:
        output: JsonObject = await tool.run(arguments)
    except ToolFailed as error:
        return {**result, "is_error": True, "content": str(error)}
    except Exception:
        logger.exception("Assistant tool %s failed", tool.name)
        return {**result, "is_error": True, "content": "No se pudo leer ese dato ahora."}
    return {**result, "content": json.dumps(output, ensure_ascii=False, default=str)}


class ClaudeAssistant:
    def __init__(
        self,
        *,
        api_key: str,
        model: str = DEFAULT_MODEL,
        effort: Effort = "medium",
        client: anthropic.AsyncAnthropic | None = None,
    ) -> None:
        self._client = client or anthropic.AsyncAnthropic(
            api_key=api_key, timeout=TIMEOUT_SECONDS, max_retries=2
        )
        self._model = model
        self._effort = effort

    async def reply(
        self,
        *,
        person: PersonContext,
        history: Sequence[JsonObject],
        question: str,
        tools: Sequence[AssistantTool],
    ) -> AsyncIterator[AssistantEvent]:
        by_name = {tool.name: tool for tool in tools}
        params = [_tool_param(tool) for tool in tools]
        system = [
            {"type": "text", "text": GUIDE},
            {"type": "text", "text": person_context(person)},
        ]
        messages: list[JsonObject] = [*history, {"role": "user", "content": question}]
        json_retries = 0
        steps = 0
        while steps < MAX_STEPS:
            try:
                async with self._client.beta.messages.stream(
                    model=self._model,
                    max_tokens=MAX_TOKENS,
                    system=system,  # type: ignore[arg-type]
                    tools=params,  # type: ignore[arg-type]
                    messages=messages,  # type: ignore[arg-type]
                    output_config={"effort": self._effort},
                    cache_control={"type": "ephemeral"},
                    betas=[FALLBACK_BETA],
                    fallbacks="default",
                ) as stream:
                    async for event in stream:
                        if event.type == "text":
                            yield TextChunk(event.text)
                    final = await stream.get_final_message()
            except ValueError:
                # A tool input the SDK could not parse at all: there is no tool_use id to
                # answer, so ask again (bounded). API errors are not ValueError.
                json_retries += 1
                if json_retries > MAX_JSON_RETRIES:
                    raise AssistantUnavailable("Tool input could not be parsed") from None
                continue
            except anthropic.APIError as error:
                raise AssistantUnavailable(f"Claude failed: {type(error).__name__}") from error
            json_retries = 0
            steps += 1

            if final.stop_reason == "refusal":
                # The whole fallback chain declined: nothing usable to keep or show.
                raise AssistantUnavailable("Claude declined the request")
            messages.append({"role": "assistant", "content": final.to_dict(mode="json")["content"]})
            if final.stop_reason == "pause_turn":
                continue
            uses = [block for block in final.content if block.type == "tool_use"]
            if not uses:
                yield Answered(model_state=tuple(messages))
                return
            if final.stop_reason == "max_tokens":
                raise AssistantUnavailable("A tool input was cut off by max_tokens")
            for status in dict.fromkeys(by_name[b.name].status for b in uses if b.name in by_name):
                yield ToolUsed(status)
            # Every result of this turn goes back in one user message.
            results = [await _run(by_name.get(block.name), block) for block in uses]
            messages.append({"role": "user", "content": results})
        raise AssistantUnavailable("Too many tool rounds")


class DisabledAssistant:
    """No Anthropic key: every question gets the fallback reply."""

    async def reply(
        self,
        *,
        person: PersonContext,
        history: Sequence[JsonObject],
        question: str,
        tools: Sequence[AssistantTool],
    ) -> AsyncIterator[AssistantEvent]:
        raise AssistantUnavailable("No Anthropic key configured")
        yield  # pragma: no cover - makes this an async generator
