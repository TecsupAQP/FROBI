"""Each role gets its own lookups, always bound to the person asking (RNF08)."""

from uuid import uuid4

import pytest

from fakes.assistant import FakeStudyData
from frobi.modules.assistant.application.ports import ToolFailed
from frobi.modules.assistant.application.tools import (
    MAX_GUIDE_CHARS,
    learner_tools,
    teacher_tools,
)

ANA, MARISOL, GUIDE, CLASS = uuid4(), uuid4(), uuid4(), uuid4()


@pytest.fixture
def data() -> FakeStudyData:
    return FakeStudyData(ANA, MARISOL, GUIDE, CLASS)


def test_learners_cannot_reach_class_data(data: FakeStudyData) -> None:
    names = {tool.name for tool in learner_tools(data, ANA, None)}

    assert names == {"list_my_guides", "read_guide", "my_progress"}


def test_teachers_get_their_classes_but_not_a_learner_progress(data: FakeStudyData) -> None:
    names = {tool.name for tool in teacher_tools(data, MARISOL, None)}

    assert names == {
        "list_my_guides",
        "read_guide",
        "my_classes",
        "class_dashboard",
        "student_detail",
    }


async def test_progress_is_always_the_askers_own(data: FakeStudyData) -> None:
    tool = next(t for t in learner_tools(data, ANA, None) if t.name == "my_progress")

    # Whatever the model sends, it reads the person who asked.
    result = await tool.run({"person_id": str(uuid4())})

    assert result["owner"] == str(ANA)


async def test_read_guide_starts_with_the_table_of_contents(data: FakeStudyData) -> None:
    tool = next(t for t in learner_tools(data, ANA, GUIDE) if t.name == "read_guide")

    contents = await tool.run({})

    assert [t["title"] for t in contents["topics"]] == ["Inductivos", "Capacitivos"]
    assert all("text" not in t for t in contents["topics"])


async def test_read_guide_reads_one_topic_of_the_open_guide(data: FakeStudyData) -> None:
    tool = next(t for t in learner_tools(data, ANA, GUIDE) if t.name == "read_guide")

    topic = await tool.run({"topic": 1})

    assert topic["text"] == data.guide_text
    assert topic["pages"] == "1-2"
    with pytest.raises(ToolFailed, match="tema 9"):
        await tool.run({"topic": 9})


async def test_read_guide_without_an_open_guide_explains_what_to_do(data: FakeStudyData) -> None:
    tool = next(t for t in learner_tools(data, ANA, None) if t.name == "read_guide")

    with pytest.raises(ToolFailed, match="list_my_guides"):
        await tool.run({})


async def test_someone_elses_guide_is_not_found(data: FakeStudyData) -> None:
    tool = next(t for t in learner_tools(data, ANA, None) if t.name == "read_guide")

    with pytest.raises(ToolFailed):
        await tool.run({"material_id": str(uuid4())})


async def test_long_topics_are_cut_and_say_so(data: FakeStudyData) -> None:
    data.guide_text = "x" * (MAX_GUIDE_CHARS + 10)
    tool = next(t for t in learner_tools(data, ANA, GUIDE) if t.name == "read_guide")

    result = await tool.run({"topic": "1"})

    assert len(result["text"]) == MAX_GUIDE_CHARS
    assert "recortado" in result["note"]


async def test_a_class_of_another_teacher_is_not_found(data: FakeStudyData) -> None:
    tool = next(t for t in teacher_tools(data, MARISOL, None) if t.name == "class_dashboard")

    assert (await tool.run({"class_id": str(CLASS)}))["students"]
    with pytest.raises(ToolFailed):
        await tool.run({"class_id": str(uuid4())})


async def test_invalid_ids_fail_cleanly(data: FakeStudyData) -> None:
    tool = next(t for t in teacher_tools(data, MARISOL, None) if t.name == "student_detail")

    with pytest.raises(ToolFailed, match="id válido"):
        await tool.run({"class_id": "nope", "student_id": str(ANA)})
