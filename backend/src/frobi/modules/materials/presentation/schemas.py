"""M3 · Material: contract with the front."""

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.materials.domain import Material, MaterialKind, MaterialSource, Work


class MaterialSummaryOut(BaseModel):
    id: UUID
    title: str
    kind: MaterialKind
    source: MaterialSource
    preview: str = Field(description="Primeras líneas del texto.")

    @classmethod
    def from_domain(cls, material: Material) -> "MaterialSummaryOut":
        return cls(
            id=material.id,
            title=material.title,
            kind=material.kind,
            source=material.source,
            preview=material.preview(),
        )


class TopicOut(BaseModel):
    position: int = Field(description="Número del tema (desde 1); se usa en `topic` al adaptar.")
    title: str
    text: str = Field(description="Texto original del tema.")
    page_start: int | None = Field(default=None, description="Página donde empieza (PDF).")
    page_end: int | None = Field(default=None, description="Página donde termina (PDF).")


class MaterialOut(BaseModel):
    id: UUID
    title: str
    kind: MaterialKind
    source: MaterialSource
    class_id: UUID | None
    extracted_text: str
    created_at: datetime
    has_file: bool = Field(
        default=False,
        description="Hay un PDF original para la vista previa (`GET /materials/{id}/file`).",
    )
    topics: list[TopicOut] = Field(
        default_factory=list,
        description="Temas del material, de un tamaño que la IA procesa en una sola petición.",
    )

    @classmethod
    def from_domain(cls, material: Material) -> "MaterialOut":
        return cls(
            id=material.id,
            title=material.title,
            kind=material.kind,
            source=material.source,
            class_id=material.class_id,
            extracted_text=material.text,
            created_at=material.created_at,
            has_file=material.has_file,
            topics=[
                TopicOut(
                    position=t.position,
                    title=t.title,
                    text=t.text,
                    page_start=t.page_start,
                    page_end=t.page_end,
                )
                for t in material.topics()
            ],
        )


class MaterialFileOut(BaseModel):
    url: str = Field(description="Enlace temporal al PDF original; se abre sin token.")
    expires_in: int = Field(description="Segundos que dura el enlace.")


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

    @classmethod
    def from_domain(cls, work: Work) -> "WorkOut":
        return cls(
            id=work.id,
            brief_material_id=work.brief_material_id,
            draft_material_id=work.draft_material_id,
            organized=OrganizedWork(
                requirements=list(work.organized.requirements),
                topics=list(work.organized.topics),
                missing=list(work.organized.missing),
            ),
        )
