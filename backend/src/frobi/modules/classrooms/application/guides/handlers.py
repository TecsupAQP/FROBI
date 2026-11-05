"""Guías de la clase: el docente decide si cada material es de estudio o tiene tareas, y ambos
ven cuánto avanzó cada alumno. Solo cuenta lo hecho dentro de la clase (RNF16)."""

from dataclasses import dataclass
from uuid import UUID

from frobi.modules.classrooms.application.manage_class import GetClassHandler, own_class
from frobi.modules.classrooms.application.ports import (
    ClassMaterial,
    ClassMaterials,
    ClassRepository,
    GuideActivityReader,
    GuidePlanRepository,
    MembershipRepository,
    PersonDirectory,
)
from frobi.modules.classrooms.domain import (
    GuideMode,
    GuideNotFound,
    GuidePlan,
    GuideProgress,
    MembershipStatus,
)
from frobi.shared.application import UnitOfWork

from .progress import guide_progress


@dataclass(frozen=True, slots=True)
class SaveGuidePlanCommand:
    teacher_id: UUID
    class_id: UUID
    material_id: UUID
    mode: GuideMode
    tasks: list[str]


class SaveGuidePlanHandler:
    """Solo el docente de la clase, y solo sobre material de esa clase."""

    def __init__(
        self,
        uow: UnitOfWork,
        classes: ClassRepository,
        materials: ClassMaterials,
        plans: GuidePlanRepository,
    ) -> None:
        self._uow = uow
        self._classes = classes
        self._materials = materials
        self._plans = plans

    async def handle(self, command: SaveGuidePlanCommand) -> GuidePlan:
        await own_class(self._classes, command.teacher_id, command.class_id)
        content = await self._materials.list_for_class(command.class_id)
        if all(material.id != command.material_id for material in content):
            raise GuideNotFound()
        current = await self._plans.get(command.material_id)
        plan = GuidePlan.create(
            command.material_id,
            command.class_id,
            command.mode,
            command.tasks,
            existing=current.tasks if current else (),
        )
        async with self._uow:
            await self._plans.save(plan)
            await self._uow.commit()
        return plan


@dataclass(frozen=True, slots=True)
class ClassGuide:
    material: ClassMaterial
    plan: GuidePlan


async def _guides(
    materials: ClassMaterials, plans: GuidePlanRepository, class_id: UUID
) -> list[ClassGuide]:
    by_material = {plan.material_id: plan for plan in await plans.list_for_class(class_id)}
    return [
        ClassGuide(
            material, by_material.get(material.id) or GuidePlan.default(material.id, class_id)
        )
        for material in await materials.list_for_class(class_id)
    ]


class ListClassGuidesHandler:
    """El contenido de la clase con su tipo y tareas: lo ven el docente y los alumnos unidos."""

    def __init__(
        self, get_class: GetClassHandler, materials: ClassMaterials, plans: GuidePlanRepository
    ) -> None:
        self._get_class = get_class
        self._materials = materials
        self._plans = plans

    async def handle(self, person_id: UUID, class_id: UUID) -> list[ClassGuide]:
        await self._get_class.handle(person_id, class_id)
        return await _guides(self._materials, self._plans, class_id)


class MyGuidesProgressHandler:
    """El avance de la persona en cada guía de su clase."""

    def __init__(
        self,
        get_class: GetClassHandler,
        materials: ClassMaterials,
        plans: GuidePlanRepository,
        activity: GuideActivityReader,
    ) -> None:
        self._get_class = get_class
        self._materials = materials
        self._plans = plans
        self._activity = activity

    async def handle(self, person_id: UUID, class_id: UUID) -> list[GuideProgress]:
        await self._get_class.handle(person_id, class_id)
        guides = await _guides(self._materials, self._plans, class_id)
        activity = await self._activity.read(class_id)
        return [
            guide_progress(
                guide.plan, person_id, activity.adaptations, activity.questions, activity.attempts
            )
            for guide in guides
        ]


@dataclass(frozen=True, slots=True)
class StudentGuideProgress:
    person_id: UUID
    alias: str
    progress: GuideProgress


@dataclass(frozen=True, slots=True)
class GuideClassProgress:
    guide: ClassGuide
    students: list[StudentGuideProgress]


class ClassGuidesProgressHandler:
    """Para el docente: el avance de cada alumno en cada guía (detecta a tiempo, no califica)."""

    def __init__(
        self,
        classes: ClassRepository,
        memberships: MembershipRepository,
        people: PersonDirectory,
        materials: ClassMaterials,
        plans: GuidePlanRepository,
        activity: GuideActivityReader,
    ) -> None:
        self._classes = classes
        self._memberships = memberships
        self._people = people
        self._materials = materials
        self._plans = plans
        self._activity = activity

    async def handle(self, teacher_id: UUID, class_id: UUID) -> list[GuideClassProgress]:
        await own_class(self._classes, teacher_id, class_id)
        guides = await _guides(self._materials, self._plans, class_id)
        activity = await self._activity.read(class_id)
        joined = [
            m
            for m in await self._memberships.for_class(class_id)
            if m.status is MembershipStatus.JOINED and m.person_id is not None
        ]
        result = []
        for guide in guides:
            students = []
            for membership in joined:
                assert membership.person_id is not None
                progress = guide_progress(
                    guide.plan,
                    membership.person_id,
                    activity.adaptations,
                    activity.questions,
                    activity.attempts,
                )
                alias = await self._people.alias_of(membership.person_id) or membership.alias
                students.append(StudentGuideProgress(membership.person_id, alias, progress))
            result.append(GuideClassProgress(guide, students))
        return result
