"""Score a prompt piece by piece and propose a better one (RF09, RF10, RF12, RF23)."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.prompt_coach.application.ports import (
    EvaluationRepository,
    MaterialLookup,
    PromptScorer,
)
from frobi.modules.prompt_coach.domain import (
    MaterialNotAvailable,
    PromptEvaluation,
    clean_prompt,
    piece_scores,
)
from frobi.shared.application import UnitOfWork
from frobi.shared.domain import Clock


@dataclass(frozen=True, slots=True)
class EvaluatePromptCommand:
    person_id: UUID
    class_id: UUID | None
    text: str
    material_id: UUID | None = None
    claim_id: UUID | None = None


class EvaluatePromptHandler:
    def __init__(
        self,
        uow: UnitOfWork,
        evaluations: EvaluationRepository,
        materials: MaterialLookup,
        scorer: PromptScorer,
        clock: Clock,
    ) -> None:
        self._uow = uow
        self._evaluations = evaluations
        self._materials = materials
        self._scorer = scorer
        self._clock = clock

    async def handle(self, command: EvaluatePromptCommand) -> PromptEvaluation:
        prompt = clean_prompt(command.text)
        material = None
        if command.material_id is not None:
            material = await self._materials.find(command.person_id, command.material_id)
            if material is None:
                raise MaterialNotAvailable()
        draft = await self._scorer.score(
            requested_by=command.person_id, prompt=prompt, material=material
        )
        evaluation = PromptEvaluation.create(
            person_id=command.person_id,
            class_id=command.class_id,
            text=prompt,
            scores=piece_scores(draft.scores, draft.feedback),
            improved_text=draft.improved_text,
            material_id=command.material_id,
            claim_id=command.claim_id,
            now=self._clock.now(),
        )
        async with self._uow:
            await self._evaluations.add(evaluation)
            await self._uow.commit()
        return evaluation
