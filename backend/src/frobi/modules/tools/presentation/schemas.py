"""M10 · Herramientas recomendadas: contract with the front."""

from uuid import UUID

from pydantic import BaseModel, Field


class ToolOut(BaseModel):
    id: str = Field(examples=["google-scholar"])
    name: str
    need: str = Field(description="Necesidad que cubre, para filtrar con `?need=`.")
    use_for: str
    avoid_for: str


class RecommendationRequest(BaseModel):
    need: str | None = Field(default=None, max_length=60, examples=["verify_source"])
    claim_id: UUID | None = Field(
        default=None, description="Afirmación de M9 para la que se busca herramienta."
    )


class RecommendationOut(BaseModel):
    tool: ToolOut
    why: str
    when_not: str
