"""M3 · Material: contract with the front."""

from datetime import datetime
from enum import StrEnum
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class MaterialKind(StrEnum):
    GUIDE = "guide"
    BRIEF = "brief"
    DRAFT = "draft"
    CLASS_CONTENT = "class_content"


class MaterialSource(StrEnum):
    SAMPLE = "sample"
    UPLOAD = "upload"
    PASTE = "paste"


class MaterialSummaryOut(BaseModel):
    id: UUID
    title: str
    kind: MaterialKind
    source: MaterialSource
    preview: str = Field(description="Primeras líneas del texto.")


class MaterialOut(BaseModel):
    id: UUID
    title: str
    kind: MaterialKind
    source: MaterialSource
    class_id: UUID | None
    extracted_text: str
    created_at: datetime


class CreateMaterialRequest(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    kind: Literal["guide", "brief", "draft"]
    text: str = Field(min_length=1, max_length=100_000)


class CreateWorkRequest(BaseModel):
    brief_material_id: UUID = Field(description="Material con `kind=brief` (la consigna).")
    draft_material_id: UUID = Field(description="Material con `kind=draft` (el borrador).")


class OrganizedWork(BaseModel):
    requirements: list[str] = Field(description="Lo que pide la consigna.")
    topics: list[str] = Field(description="Temas que aparecen en el borrador.")
    missing: list[str] = Field(description="Requisitos que el borrador todavía no cubre.")


class WorkOut(BaseModel):
    id: UUID
    brief_material_id: UUID
    draft_material_id: UUID
    organized: OrganizedWork
