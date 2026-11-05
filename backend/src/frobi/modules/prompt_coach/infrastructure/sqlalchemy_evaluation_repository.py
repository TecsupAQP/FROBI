from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules.prompt_coach.domain import PieceScore, PromptEvaluation, RecipePiece

from .models import PromptEvaluationModel


class SqlAlchemyEvaluationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, evaluation: PromptEvaluation) -> None:
        self._session.add(
            PromptEvaluationModel(
                id=evaluation.id,
                person_id=evaluation.person_id,
                class_id=evaluation.class_id,
                text=evaluation.text,
                scores=[
                    {"piece": s.piece.value, "score": s.score, "feedback": s.feedback}
                    for s in evaluation.scores
                ],
                improved_text=evaluation.improved_text,
                total=evaluation.total,
                autonomy_level=evaluation.autonomy_level,
                material_id=evaluation.material_id,
                claim_id=evaluation.claim_id,
                created_at=evaluation.created_at,
            )
        )

    async def get(self, evaluation_id: UUID) -> PromptEvaluation | None:
        row = await self._session.get(PromptEvaluationModel, evaluation_id)
        if row is None:
            return None
        return PromptEvaluation(
            id=row.id,
            person_id=row.person_id,
            class_id=row.class_id,
            text=row.text,
            scores=tuple(
                PieceScore(RecipePiece(s["piece"]), int(s["score"]), str(s["feedback"]))
                for s in row.scores
            ),
            improved_text=row.improved_text,
            material_id=row.material_id,
            claim_id=row.claim_id,
            created_at=row.created_at,
        )
