from uuid import UUID

from frobi.modules.tutoring.application.ports import Hint, TutoringContext
from frobi.modules.tutoring.domain import HelpAttempt, HelpStep

ADAPTATION_ID = UUID("00000000-0000-4000-8000-0000000000d9")
CONTEXT = TutoringContext(
    adaptation_id=ADAPTATION_ID,
    material_title="Guía",
    material_text=(
        "## Sensores capacitivos\n"
        "Los sensores capacitivos detectan plásticos y líquidos a través de un tanque."
    ),
    adapted_text="Versión adaptada",
)


class InMemoryAttempts:
    def __init__(self) -> None:
        self.items: dict[UUID, HelpAttempt] = {}
        self.locked: list[UUID] = []

    async def add(self, attempt: HelpAttempt) -> None:
        self.items[attempt.id] = attempt

    async def get(self, attempt_id: UUID, *, for_update: bool = False) -> HelpAttempt | None:
        if for_update:
            self.locked.append(attempt_id)
        return self.items.get(attempt_id)

    async def save(self, attempt: HelpAttempt) -> None:
        self.items[attempt.id] = attempt


class StaticContexts:
    def __init__(self, owner: UUID) -> None:
        self._owner = owner

    async def get(self, person_id: UUID, adaptation_id: UUID) -> TutoringContext | None:
        if person_id == self._owner and adaptation_id == ADAPTATION_ID:
            return CONTEXT
        return None


class EchoHints:
    def __init__(self) -> None:
        self.asked: list[HelpStep] = []

    async def hint(
        self, *, requested_by: UUID, context: TutoringContext, task_ref: str, step: HelpStep
    ) -> Hint:
        self.asked.append(step)
        return Hint(text=f"ayuda {step.value}", fallback=False)
