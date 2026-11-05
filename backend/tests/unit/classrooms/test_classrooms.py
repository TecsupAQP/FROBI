from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from fakes.identity import FakeUnitOfWork, FixedClock
from frobi.modules.classrooms.application import (
    ActiveClassHandler,
    CreateClassCommand,
    CreateClassHandler,
    GetClassHandler,
    InviteStudentsHandler,
    JoinClassHandler,
    LeaveClassHandler,
    ListClassContentHandler,
    ListMembersHandler,
    ListMyClassesHandler,
    UploadClassContentCommand,
    UploadClassContentHandler,
)
from frobi.modules.classrooms.application.demo import DemoPeopleHandler
from frobi.modules.classrooms.application.ports import ClassMaterial
from frobi.modules.classrooms.domain import (
    CODE_ALPHABET,
    CODE_LENGTH,
    DEMO_CLASS_ID,
    DEMO_TEACHER_ID,
    ClassNotFound,
    Classroom,
    InvalidClassCode,
    InvalidClassData,
    Membership,
    MembershipStatus,
    MissingClassContent,
    NotInAClass,
    TeachersOnly,
    new_invite_code,
)

TEACHER, ANA, LUIS = uuid4(), uuid4(), uuid4()


class Classes:
    def __init__(self) -> None:
        self.items: dict[UUID, Classroom] = {}

    async def add(self, classroom: Classroom) -> None:
        self.items[classroom.id] = classroom

    async def get(self, class_id: UUID) -> Classroom | None:
        return self.items.get(class_id)

    async def get_by_code(self, code: str) -> Classroom | None:
        return next((c for c in self.items.values() if c.invite_code == code), None)

    async def code_taken(self, code: str) -> bool:
        return await self.get_by_code(code) is not None

    async def list_for_teacher(self, teacher_id: UUID) -> list[Classroom]:
        mine = [c for c in self.items.values() if c.teacher_id == teacher_id]
        return sorted(mine, key=lambda c: c.created_at, reverse=True)


class Memberships:
    def __init__(self) -> None:
        self.items: dict[UUID, Membership] = {}

    async def add(self, membership: Membership) -> None:
        self.items[membership.id] = membership

    async def save(self, membership: Membership) -> None:
        self.items[membership.id] = membership

    async def active_for(self, person_id: UUID) -> Membership | None:
        joined = [
            m
            for m in self.items.values()
            if m.person_id == person_id and m.status is MembershipStatus.JOINED
        ]
        assert len(joined) <= 1, "a person has at most one active class"
        return joined[0] if joined else None

    async def for_class(self, class_id: UUID) -> list[Membership]:
        return [m for m in self.items.values() if m.class_id == class_id]


class People:
    async def is_teacher(self, person_id: UUID) -> bool:
        return person_id == TEACHER

    async def alias_of(self, person_id: UUID) -> str | None:
        return {TEACHER: "Profe", ANA: "Ana", LUIS: "Luis"}.get(person_id)


@pytest.fixture
def classes() -> Classes:
    return Classes()


@pytest.fixture
def memberships() -> Memberships:
    return Memberships()


def _codes(*values: str):  # type: ignore[no-untyped-def]
    it = iter(values)
    return lambda: next(it)


async def _create(classes: Classes, name: str = "Sensores", code: str = "ABC234") -> Classroom:
    return await CreateClassHandler(
        FakeUnitOfWork(), classes, People(), _codes(code), FixedClock()
    ).handle(CreateClassCommand(TEACHER, name, "Instrumentación", ["Leer", " leer ", "Leer"]))


def _join(classes: Classes, memberships: Memberships) -> JoinClassHandler:
    return JoinClassHandler(FakeUnitOfWork(), classes, memberships, FixedClock())


def test_invite_codes_are_readable_and_unambiguous() -> None:
    code = new_invite_code()

    assert len(code) == CODE_LENGTH
    assert set(code) <= set(CODE_ALPHABET)
    assert not set("O0I1L") & set(CODE_ALPHABET)


async def test_a_teacher_creates_a_class_with_a_code(classes: Classes) -> None:
    classroom = await _create(classes)

    assert classroom.invite_code == "ABC234"
    assert classroom.tasks == ("Leer", "leer")
    assert classes.items[classroom.id] == classroom


async def test_a_taken_code_is_regenerated(classes: Classes) -> None:
    await _create(classes, code="AAAAAA")

    second = await CreateClassHandler(
        FakeUnitOfWork(), classes, People(), _codes("AAAAAA", "BBBBBB"), FixedClock()
    ).handle(CreateClassCommand(TEACHER, "Otra", "Física", []))

    assert second.invite_code == "BBBBBB"


async def test_only_teachers_create_classes(classes: Classes) -> None:
    with pytest.raises(TeachersOnly):
        await CreateClassHandler(
            FakeUnitOfWork(), classes, People(), _codes("X"), FixedClock()
        ).handle(CreateClassCommand(ANA, "Mía", "Física", []))


async def test_blank_class_data_is_rejected(classes: Classes) -> None:
    with pytest.raises(InvalidClassData):
        await _create(classes, name="   ")


async def test_joining_with_a_code_is_case_and_space_insensitive(
    classes: Classes, memberships: Memberships
) -> None:
    classroom = await _create(classes)

    joined = await _join(classes, memberships).handle(ANA, "Ana", " abc 234 ")
    active = await ActiveClassHandler(classes, memberships).handle(ANA)

    assert joined.class_id == classroom.id
    assert active is not None
    assert active.class_name == "Sensores"


async def test_an_unknown_code_is_rejected(classes: Classes, memberships: Memberships) -> None:
    with pytest.raises(InvalidClassCode):
        await _join(classes, memberships).handle(ANA, "Ana", "NOPE99")


async def test_joining_twice_is_harmless(classes: Classes, memberships: Memberships) -> None:
    await _create(classes)
    join = _join(classes, memberships)

    await join.handle(ANA, "Ana", "ABC234")
    await join.handle(ANA, "Ana", "ABC234")

    assert len(memberships.items) == 1


async def test_joining_another_class_leaves_the_previous_one(
    classes: Classes, memberships: Memberships
) -> None:
    first = await _create(classes, code="AAA222")
    second = await _create(classes, "Física", code="BBB333")
    join = _join(classes, memberships)

    await join.handle(ANA, "Ana", "AAA222")
    await join.handle(ANA, "Ana", "BBB333")

    statuses = {m.class_id: m.status for m in memberships.items.values()}
    assert statuses == {first.id: MembershipStatus.LEFT, second.id: MembershipStatus.JOINED}


async def test_an_invitation_is_taken_by_the_person_with_that_alias(
    classes: Classes, memberships: Memberships
) -> None:
    classroom = await _create(classes)
    invite = InviteStudentsHandler(FakeUnitOfWork(), classes, memberships, FixedClock())

    invited = await invite.handle(TEACHER, classroom.id, ["Ana", "ana ", "Rosa", " "])
    await _join(classes, memberships).handle(ANA, "ANA", "ABC234")
    view = await ListMembersHandler(classes, memberships).handle(TEACHER, classroom.id)

    assert [m.alias for m in invited] == ["Ana", "Rosa"]
    by_alias = {m.alias: m for m in view.members}
    assert by_alias["Ana"].status is MembershipStatus.JOINED
    assert by_alias["Ana"].person_id == ANA
    assert by_alias["Rosa"].status_label == "Invitación pendiente"
    assert view.invite_code == "ABC234"


async def test_only_the_teacher_of_the_class_manages_it(
    classes: Classes, memberships: Memberships
) -> None:
    classroom = await _create(classes)

    with pytest.raises(ClassNotFound):
        await ListMembersHandler(classes, memberships).handle(ANA, classroom.id)
    with pytest.raises(ClassNotFound):
        await InviteStudentsHandler(FakeUnitOfWork(), classes, memberships, FixedClock()).handle(
            ANA, classroom.id, ["Luis"]
        )


async def test_the_class_is_visible_to_its_teacher_and_members_only(
    classes: Classes, memberships: Memberships
) -> None:
    classroom = await _create(classes)
    await _join(classes, memberships).handle(ANA, "Ana", "ABC234")
    get = GetClassHandler(classes, memberships)

    assert await get.handle(TEACHER, classroom.id) == classroom
    assert await get.handle(ANA, classroom.id) == classroom
    with pytest.raises(ClassNotFound):
        await get.handle(LUIS, classroom.id)


async def test_leaving_ends_the_active_class(classes: Classes, memberships: Memberships) -> None:
    await _create(classes)
    await _join(classes, memberships).handle(ANA, "Ana", "ABC234")
    leave = LeaveClassHandler(FakeUnitOfWork(), memberships, FixedClock())

    await leave.handle(ANA)

    assert await ActiveClassHandler(classes, memberships).handle(ANA) is None
    with pytest.raises(NotInAClass):
        await leave.handle(ANA)


class ClassContent:
    def __init__(self) -> None:
        self.items: list[ClassMaterial] = []

    def _add(self, class_id: UUID, title: str, text: str) -> ClassMaterial:
        material = ClassMaterial(
            uuid4(), class_id, title, text, text[:20], datetime(2026, 11, 6, tzinfo=UTC)
        )
        self.items.append(material)
        return material

    async def add_text(
        self, teacher_id: UUID, class_id: UUID, title: str, text: str
    ) -> ClassMaterial:
        return self._add(class_id, title, text)

    async def add_pdf(
        self, teacher_id: UUID, class_id: UUID, title: str, data: bytes
    ) -> ClassMaterial:
        return self._add(class_id, title, data.decode())

    async def list_for_class(self, class_id: UUID) -> list[ClassMaterial]:
        return [m for m in self.items if m.class_id == class_id]


async def test_the_teacher_uploads_text_or_a_pdf_to_their_class(classes: Classes) -> None:
    classroom = await _create(classes)
    content = ClassContent()
    upload = UploadClassContentHandler(classes, content)

    pasted = await upload.handle(UploadClassContentCommand(TEACHER, classroom.id, "Guía", "Texto"))
    pdf = await upload.handle(UploadClassContentCommand(TEACHER, classroom.id, "PDF", pdf=b"Hoja"))

    assert (pasted.text, pdf.text) == ("Texto", "Hoja")
    assert content.items == [pasted, pdf]


@pytest.mark.parametrize(("text", "pdf"), [(None, None), ("  ", None), ("Texto", b"PDF")])
async def test_class_content_needs_exactly_one_of_text_or_pdf(
    classes: Classes, text: str | None, pdf: bytes | None
) -> None:
    classroom = await _create(classes)

    with pytest.raises(MissingClassContent):
        await UploadClassContentHandler(classes, ClassContent()).handle(
            UploadClassContentCommand(TEACHER, classroom.id, "Guía", text, pdf)
        )


async def test_nobody_but_the_teacher_of_the_class_uploads(classes: Classes) -> None:
    classroom = await _create(classes)
    content = ClassContent()

    with pytest.raises(ClassNotFound):
        await UploadClassContentHandler(classes, content).handle(
            UploadClassContentCommand(ANA, classroom.id, "Guía", "Texto")
        )
    assert content.items == []


async def test_class_content_is_for_the_teacher_and_joined_students_only(
    classes: Classes, memberships: Memberships
) -> None:
    classroom = await _create(classes)
    content = ClassContent()
    await UploadClassContentHandler(classes, content).handle(
        UploadClassContentCommand(TEACHER, classroom.id, "Guía", "Texto")
    )
    await _join(classes, memberships).handle(ANA, "Ana", classroom.invite_code)
    listing = ListClassContentHandler(GetClassHandler(classes, memberships), content)

    assert [m.title for m in await listing.handle(TEACHER, classroom.id)] == ["Guía"]
    assert [m.title for m in await listing.handle(ANA, classroom.id)] == ["Guía"]
    with pytest.raises(ClassNotFound):
        await listing.handle(LUIS, classroom.id)


async def test_a_teacher_lists_their_own_classes_only(classes: Classes) -> None:
    mine = await _create(classes, "Sensores", "ABC234")
    other = Classroom.create(
        teacher_id=uuid4(),
        name="Otra",
        subject="Redes",
        tasks=[],
        invite_code="XYZ789",
        now=datetime(2026, 11, 6, tzinfo=UTC),
    )
    await classes.add(other)

    assert await ListMyClassesHandler(classes, People()).handle(TEACHER) == [mine]
    with pytest.raises(TeachersOnly):
        await ListMyClassesHandler(classes, People()).handle(ANA)


async def test_demo_people_are_the_demo_teacher_and_the_seeded_students(
    memberships: Memberships,
) -> None:
    ana = uuid4()
    await memberships.add(
        Membership.join_new(
            class_id=DEMO_CLASS_ID,
            person_id=ana,
            alias="Ana (demo)",
            now=datetime(2026, 11, 6, tzinfo=UTC),
        )
    )
    demo = DemoPeopleHandler(memberships)

    assert await demo.person_for("teacher") == DEMO_TEACHER_ID
    assert await demo.person_for("ana") == ana
    assert await demo.person_for("luis") is None
    assert await demo.person_for("someone") is None
