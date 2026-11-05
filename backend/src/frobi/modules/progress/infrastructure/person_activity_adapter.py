"""PersonActivityReader over the public APIs of the modules that record activity."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from frobi.modules import adaptations, comprehension, prompt_coach, tutoring
from frobi.modules.progress.application.ports import PersonActivity, RecipeView


class PersonActivityReaderAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read(self, person_id: UUID) -> PersonActivity:
        recipe = await adaptations.latest_recipe_of_person(self._session, person_id)
        return PersonActivity(
            formats=await adaptations.format_uses_of_person(self._session, person_id),
            help=await tutoring.help_of_person(self._session, person_id),
            answers=await comprehension.answers_of_person(self._session, person_id),
            prompt_scores=await prompt_coach.scores_of_person(self._session, person_id),
            latest_recipe=None
            if recipe is None
            else RecipeView(recipe.context, recipe.goal, recipe.level, recipe.format.value),
        )
