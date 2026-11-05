"""M13 · Ajustes y privacidad.

Real: GET and PATCH /me/settings. The rest are stubs that return example data until phase 2.
"""

from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, status

from frobi.modules.settings.application import (
    GetSettingsHandler,
    UpdateSettingsCommand,
    UpdateSettingsHandler,
)
from frobi.modules.settings.domain import TOGGLES, Language
from frobi.shared.presentation import AUTH_RESPONSES, CurrentPersonId, problem, require_token

from .dependencies import get_get_settings, get_update_settings
from .schemas import (
    AccountOut,
    AliasPatch,
    LanguageOut,
    PrivacyItem,
    PrivacyOut,
    SettingsOut,
    SettingsPatch,
)

router = APIRouter(
    tags=["M13 · Ajustes y privacidad"],
    dependencies=[Depends(require_token)],
    responses=AUTH_RESPONSES,
)

EXAMPLE_PERSON_ID = UUID("00000000-0000-4000-8000-000000000001")


@router.get("/me/settings", summary="Ajustes actuales")
async def get_settings(
    person_id: CurrentPersonId,
    handler: Annotated[GetSettingsHandler, Depends(get_get_settings)],
) -> SettingsOut:
    return SettingsOut.from_domain(await handler.handle(person_id))


@router.patch(
    "/me/settings",
    summary="Cambiar interruptores de accesibilidad e idioma",
    responses={422: problem("Valor inválido o idioma todavía no disponible.")},
)
async def update_settings(
    body: SettingsPatch,
    person_id: CurrentPersonId,
    handler: Annotated[UpdateSettingsHandler, Depends(get_update_settings)],
) -> SettingsOut:
    sent = body.model_dump(exclude_none=True)
    updated = await handler.handle(
        UpdateSettingsCommand(
            person_id=person_id,
            toggles={name: sent[name] for name in TOGGLES if name in sent},
            language=body.language,
        )
    )
    return SettingsOut.from_domain(updated)


@router.patch("/me", summary="Cambiar el alias")
async def update_alias(body: AliasPatch) -> AccountOut:
    return AccountOut(id=EXAMPLE_PERSON_ID, alias=body.alias, career="Mecatrónica", role="learner")


@router.delete(
    "/me/membership",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Salir de la clase (lo que hagas después queda fuera de la clase)",
)
async def leave_class() -> None:
    return None


@router.get("/me/privacy", summary="Qué ve tu docente")
async def get_privacy() -> PrivacyOut:
    return PrivacyOut(
        in_class=True,
        class_name="Sensores 2026-II",
        shared_with_teacher=[
            PrivacyItem(category="formats", description="Qué formatos usaste en la clase."),
            PrivacyItem(category="answers", description="Aciertos en las preguntas de la clase."),
            PrivacyItem(category="help", description="Hasta qué escalón de ayuda llegaste."),
        ],
        never_shared=[
            PrivacyItem(category="outside_class", description="Lo que haces fuera de la clase."),
            PrivacyItem(category="drafts", description="El texto de tus borradores."),
            PrivacyItem(category="profiles", description="Tus perfiles de accesibilidad."),
        ],
    )


@router.get("/languages", summary="Idiomas de la interfaz")
async def list_languages() -> list[LanguageOut]:
    return [
        LanguageOut(code=Language.ES, name="Español", status="available"),
        LanguageOut(code=Language.QU, name="Quechua", status="coming_soon"),
        LanguageOut(code=Language.AY, name="Aimara", status="coming_soon"),
    ]
