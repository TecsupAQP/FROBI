"""M13 · Ajustes y privacidad.

Ajustes, alias, salir de la clase, «Qué ve tu docente» e idiomas (`es` disponible).
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from frobi.modules.settings.application import (
    GetSettingsHandler,
    LeaveClassHandler,
    PrivacyHandler,
    RenameHandler,
    UpdateSettingsCommand,
    UpdateSettingsHandler,
)
from frobi.modules.settings.domain import TOGGLES, Language
from frobi.shared.presentation import AUTH_RESPONSES, CurrentPersonId, problem, require_token

from .dependencies import (
    get_get_settings,
    get_leave_class,
    get_privacy_handler,
    get_rename,
    get_update_settings,
)
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


@router.patch(
    "/me",
    summary="Cambiar el alias",
    responses={422: problem("Alias vacío o de más de 40 caracteres.")},
)
async def update_alias(
    body: AliasPatch,
    person_id: CurrentPersonId,
    handler: Annotated[RenameHandler, Depends(get_rename)],
) -> AccountOut:
    account = await handler.handle(person_id, body.alias)
    return AccountOut(
        id=account.id,
        alias=account.alias,
        career=account.career,
        role=account.role,  # type: ignore[arg-type]
    )


@router.delete(
    "/me/membership",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Salir de la clase (lo que hagas después queda fuera de la clase)",
    responses={409: problem("No estás en ninguna clase (`Classrooms.NotInAClass`).")},
)
async def leave_class(
    person_id: CurrentPersonId,
    handler: Annotated[LeaveClassHandler, Depends(get_leave_class)],
) -> None:
    await handler.handle(person_id)


@router.get("/me/privacy", summary="Qué ve tu docente")
async def get_privacy(
    person_id: CurrentPersonId,
    handler: Annotated[PrivacyHandler, Depends(get_privacy_handler)],
) -> PrivacyOut:
    view = await handler.handle(person_id)
    return PrivacyOut(
        in_class=view.in_class,
        class_name=view.class_name,
        shared_with_teacher=[
            PrivacyItem(category=i.category, description=i.description)
            for i in view.shared_with_teacher
        ],
        never_shared=[
            PrivacyItem(category=i.category, description=i.description) for i in view.never_shared
        ],
    )


@router.get("/languages", summary="Idiomas de la interfaz")
async def list_languages() -> list[LanguageOut]:
    return [
        LanguageOut(code=Language.ES, name="Español", status="available"),
        LanguageOut(code=Language.QU, name="Quechua", status="coming_soon"),
        LanguageOut(code=Language.AY, name="Aimara", status="coming_soon"),
    ]
