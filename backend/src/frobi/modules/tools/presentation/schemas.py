"""M10 · Herramientas recomendadas: contract with the front."""

from uuid import UUID

from pydantic import BaseModel, Field

from frobi.modules.tools.domain import Recommendation, Tool


class ToolOut(BaseModel):
    id: str = Field(examples=["google-scholar"])
    name: str
    need: str = Field(
        description="Necesidad que cubre, para filtrar con `?need=`: verify_source, "
        "study_material, calculate, write o visualize."
    )
    use_for: str
    avoid_for: str

    @classmethod
    def from_domain(cls, tool: Tool) -> "ToolOut":
        return cls(
            id=tool.id,
            name=tool.name,
            need=tool.need.value,
            use_for=tool.use_for,
            avoid_for=tool.avoid_for,
        )


class RecommendationRequest(BaseModel):
    need: str | None = Field(default=None, max_length=60, examples=["verify_source"])
    claim_id: UUID | None = Field(
        default=None, description="Afirmación de M9 para la que se busca herramienta."
    )


class RecommendationOut(BaseModel):
    tool: ToolOut
    why: str
    when_not: str

    @classmethod
    def from_domain(cls, recommendation: Recommendation) -> "RecommendationOut":
        return cls(
            tool=ToolOut.from_domain(recommendation.tool),
            why=recommendation.why,
            when_not=recommendation.when_not,
        )
