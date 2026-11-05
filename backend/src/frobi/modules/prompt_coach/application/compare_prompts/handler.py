"""Run the original and the improved prompt and show both results side by side (RF11)."""

import asyncio
from dataclasses import dataclass
from uuid import UUID

from frobi.modules.prompt_coach.application.ports import (
    EvaluationRepository,
    MaterialLookup,
    PromptRunner,
    RunOutput,
)
from frobi.modules.prompt_coach.domain import EvaluationNotFound, PromptEvaluation


@dataclass(frozen=True, slots=True)
class Comparison:
    evaluation: PromptEvaluation
    original: RunOutput
    improved: RunOutput

    @property
    def fallback(self) -> bool:
        return self.original.fallback or self.improved.fallback


class ComparePromptsHandler:
    def __init__(
        self, evaluations: EvaluationRepository, materials: MaterialLookup, runner: PromptRunner
    ) -> None:
        self._evaluations = evaluations
        self._materials = materials
        self._runner = runner

    async def handle(self, person_id: UUID, evaluation_id: UUID) -> Comparison:
        evaluation = await self._evaluations.get(evaluation_id)
        if evaluation is None or not evaluation.visible_to(person_id):
            raise EvaluationNotFound()
        material = None
        if evaluation.material_id is not None:
            material = await self._materials.find(person_id, evaluation.material_id)
        original, improved = await asyncio.gather(
            self._runner.run(requested_by=person_id, prompt=evaluation.text, material=material),
            self._runner.run(
                requested_by=person_id, prompt=evaluation.improved_text, material=material
            ),
        )
        return Comparison(evaluation=evaluation, original=original, improved=improved)
