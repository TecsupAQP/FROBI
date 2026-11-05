"""classrooms' ports over the public API of identity, and the shared ClassContext."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from frobi.modules import adaptations, comprehension, identity, materials, prompt_coach, tutoring
from frobi.modules.classrooms.application.ports import ClassActivity, ClassMaterial, GuideActivity
from frobi.shared.infrastructure.llm import LlmClient, PdfTranscriber

from .sqlalchemy_repositories import SqlAlchemyMembershipRepository


class ClassActivityReaderAdapter:
    """Each module's «in this class» read, through its public API (never «all activity»)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read(self, class_id: UUID) -> ClassActivity:
        return ClassActivity(
            formats=await adaptations.format_uses_in_class(self._session, class_id),
            help=await tutoring.help_in_class(self._session, class_id),
            answers=await comprehension.answers_in_class(self._session, class_id),
            prompt_scores=await prompt_coach.scores_in_class(self._session, class_id),
        )


class GuideActivityReaderAdapter:
    """What the guides' progress is made of, read «in this class» from each module (RNF16)."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def read(self, class_id: UUID) -> GuideActivity:
        guide_adaptations = await adaptations.guide_adaptations_in_class(self._session, class_id)
        return GuideActivity(
            adaptations=guide_adaptations,
            questions=await comprehension.question_results(
                self._session, [a.adaptation_id for a in guide_adaptations]
            ),
            attempts=await tutoring.task_attempts_in_class(self._session, class_id),
        )


class PersonDirectoryAdapter:
    def __init__(self, session: AsyncSession) -> None:
        self._people = identity.read_person_handler(session)

    async def is_teacher(self, person_id: UUID) -> bool:
        person = await self._people.find(person_id)
        return person is not None and person.role is identity.Role.TEACHER

    async def alias_of(self, person_id: UUID) -> str | None:
        person = await self._people.find(person_id)
        return None if person is None else person.alias


class ClassroomsClassContext:
    """Shared ``ClassContext``: the class of the person's ``joined`` membership (RNF16).

    Lives on ``app.state``, outside any request, so it opens its own short session.
    """

    def __init__(self, session_factory: async_sessionmaker[AsyncSession]) -> None:
        self._session_factory = session_factory

    async def active_class(self, person_id: UUID) -> UUID | None:
        async with self._session_factory() as session:
            membership = await SqlAlchemyMembershipRepository(session).active_for(person_id)
        return None if membership is None else membership.class_id


def _class_material(material: materials.Material) -> ClassMaterial:
    assert material.class_id is not None
    return ClassMaterial(
        id=material.id,
        class_id=material.class_id,
        title=material.title,
        text=material.text,
        preview=material.preview(),
        created_at=material.created_at,
    )


class ClassMaterialsAdapter:
    def __init__(
        self,
        session: AsyncSession,
        transcriber: PdfTranscriber | None = None,
        llm: LlmClient | None = None,
        timeout_seconds: float = 15.0,
    ) -> None:
        """Only the upload needs ``transcriber`` (scanned PDFs) and ``llm`` (topics of long
        texts with no headings)."""
        self._content = materials.class_content_handler(session, transcriber, llm, timeout_seconds)

    async def add_text(
        self, teacher_id: UUID, class_id: UUID, title: str, text: str
    ) -> ClassMaterial:
        return _class_material(await self._content.add_text(teacher_id, class_id, title, text))

    async def add_pdf(
        self, teacher_id: UUID, class_id: UUID, title: str, data: bytes
    ) -> ClassMaterial:
        return _class_material(await self._content.add_pdf(teacher_id, class_id, title, data))

    async def list_for_class(self, class_id: UUID) -> list[ClassMaterial]:
        return [_class_material(m) for m in await self._content.list_for_class(class_id)]
