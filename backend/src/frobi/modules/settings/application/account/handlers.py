"""Account part of M13: change the alias (RF52), leave the class (RF49), «Qué ve tu docente» (RF53).

The privacy list mirrors what the teacher panel really reads (classrooms' ClassActivityReader):
only activity recorded with the class's ``class_id``.
"""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.settings.application.ports import Account, AccountView, ClassMembership


class RenameHandler:
    def __init__(self, account: Account) -> None:
        self._account = account

    async def handle(self, person_id: UUID, alias: str) -> AccountView:
        return await self._account.rename(person_id, alias)


class LeaveClassHandler:
    def __init__(self, membership: ClassMembership) -> None:
        self._membership = membership

    async def handle(self, person_id: UUID) -> None:
        await self._membership.leave(person_id)


@dataclass(frozen=True, slots=True)
class PrivacyItem:
    category: str
    description: str


SHARED_IN_CLASS: tuple[PrivacyItem, ...] = (
    PrivacyItem("formats", "Qué formatos usaste dentro de la clase."),
    PrivacyItem("answers", "Tus aciertos en las preguntas que respondiste dentro de la clase."),
    PrivacyItem("help", "Hasta qué escalón de ayuda llegaste y lo que resolviste sin IA."),
    PrivacyItem("prompts", "El puntaje de tus instrucciones a la IA dentro de la clase."),
)
NEVER_SHARED: tuple[PrivacyItem, ...] = (
    PrivacyItem("outside_class", "Lo que haces fuera de la clase o después de salir de ella."),
    PrivacyItem("texts", "El texto de tus materiales, borradores y respuestas."),
    PrivacyItem("profiles", "Tus perfiles y ajustes de accesibilidad."),
    PrivacyItem("companion", "Si alguien te acompaña a configurar FROBI."),
)


@dataclass(frozen=True, slots=True)
class PrivacyView:
    in_class: bool
    class_name: str | None
    shared_with_teacher: tuple[PrivacyItem, ...]
    never_shared: tuple[PrivacyItem, ...]


class PrivacyHandler:
    def __init__(self, membership: ClassMembership) -> None:
        self._membership = membership

    async def handle(self, person_id: UUID) -> PrivacyView:
        current = await self._membership.current(person_id)
        if current is None:
            return PrivacyView(False, None, (), NEVER_SHARED)
        return PrivacyView(True, current.class_name, SHARED_IN_CLASS, NEVER_SHARED)
