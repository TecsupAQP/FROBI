# FROBI · Arquitectura del backend

> Monolito modular hexagonal con FastAPI, con la misma convención que `famas` (`docs/PLAN-Asistencias-QR.md`, §3) y `MarketjoyaBackend/src/Modules/<Mod>/{Domain,Application,Infrastructure,Presentation}`.
> Plan funcional y endpoints: [`PLAN_BACKEND.md`](./PLAN_BACKEND.md).

## 1. Principios

1. **Un solo desplegable, módulos con fronteras duras.** Hay un solo paquete Python, una carpeta por módulo y una carpeta por caso de uso.
2. **Hexagonal dentro de cada módulo.** El dominio es puro, la aplicación orquesta mediante puertos (`Protocol`) y la infraestructura y la presentación son adaptadores.
3. **Los módulos no se tocan por dentro.** Un módulo nunca importa el dominio ni la infraestructura de otro: se comunica a través de un puerto propio, que implementa un adaptador apoyado en la API pública del otro módulo.
4. **Screaming architecture.** Los nombres de carpeta dicen qué hace FROBI (`tutoring`, `claim_review`), no qué tecnología usa.
5. **Las reglas se verifican en CI** con `import-linter`; no dependen de la buena voluntad.

## 2. Estructura del repositorio

```
forbi/backend/
├── pyproject.toml            # uv, ruff, mypy, pytest, import-linter
├── alembic/                  # Migraciones
├── docker/                   # Dockerfile y compose.yml (api, postgres, redis)
├── fixtures/                 # Guía de sensores, respaldos de la IA, catálogo de herramientas
├── src/frobi/
│   ├── main.py               # create_app(): monta los routers de cada módulo
│   ├── shared/               # Building blocks, sin lógica de negocio de FROBI
│   │   ├── domain/           # Entity, ValueObject, DomainError, Clock (puerto)
│   │   ├── application/      # UnitOfWork (puerto), errores de aplicación
│   │   ├── infrastructure/   # Sesión de BD, SqlAlchemyUnitOfWork, cliente Redis, settings, cliente LLM
│   │   └── presentation/     # deps (current_person, require_role, class_context) y handlers problem+json
│   └── modules/
│       ├── identity/         # M1: alias, sesiones (token en Redis), rol
│       ├── onboarding/       # M2: asistente, perfiles, acompañante, introducción a la IA
│       ├── settings/         # M13: ajustes de accesibilidad, idioma, cuenta y «Qué ve tu docente»
│       ├── materials/        # M3: samples, pegado de texto, PDF, consigna y borrador (works)
│       ├── adaptations/      # M4 y M5: formatos, receta de 4 piezas, aviso de límites, respaldo
│       ├── tutoring/         # M6: escalera de ayuda, «Inténtalo sin IA»
│       ├── prompt_coach/     # M7: evaluación de instrucciones y autonomía
│       ├── comprehension/    # M8: preguntas, respuestas, pregunta similar sin ayuda
│       ├── claim_review/     # M9: semáforo de afirmaciones con respaldo
│       ├── tools/            # M10: catálogo fijo y recomendación
│       ├── classrooms/       # M12: clases, invitaciones, membresías, panel docente
│       ├── progress/         # M11: solo lectura sobre los demás; progreso y cierre
│       └── assistant/        # M14: chat privado con FROBI (Claude + herramientas) por WebSocket
└── tests/
    ├── unit/<modulo>/        # Dominio y casos de uso con fakes de los puertos
    ├── integration/          # Repositorios SQLAlchemy y Redis reales (testcontainers)
    └── e2e/                  # API completa con httpx.AsyncClient
```

### Módulos y responsabilidad

| Módulo | Módulos funcionales | Es dueño de (tablas o claves) | Consume (por puerto) |
| --- | --- | --- | --- |
| `identity` | M1 | `persons`, `session:*` | `classrooms.MembershipJoiner` (código opcional al entrar) |
| `onboarding` | M2 | — (orquesta) | `settings.SettingsWriter` |
| `settings` | M13 | `person_settings` | `classrooms.MembershipReader` (clase actual y salir) |
| `materials` | M3 | `materials`, `works` | — |
| `adaptations` | M4 y M5 | `adaptations`, `adapt:*`, `lock:adapt:*` | `materials.MaterialReader`, `settings.ProfileReader`, `TextGenerator` (LLM) |
| `tutoring` | M6 | `help_attempts` | `adaptations.AdaptationReader`, `HintGenerator` (LLM) |
| `prompt_coach` | M7 | `prompt_evaluations` | `PromptScorer` (LLM) |
| `comprehension` | M8 | `questions`, `answers` | `adaptations.AdaptationReader`, `QuestionGenerator` (LLM) |
| `claim_review` | M9 | `claims` | `materials.WorkReader`, `ClaimReviewer` (LLM) |
| `tools` | M10 | `tools` (seed) | — |
| `classrooms` | M12 | `classes`, `memberships`, `dashboard:*` | `ClassActivityReader` (actividad filtrada por `class_id`) |
| `progress` | M11 | — (solo lectura) | `PersonActivityReader` |
| `assistant` | M14 | `assistant:conversation:*`, `assistant:answering:*`, canales `assistant:person:*` | `StudyData` (API pública de identity, settings, materials, progress y classrooms), `AssistantModel` (Claude) |

`progress` cumple el mismo papel que `alerts` en famas: **solo lee** de los demás y no es dueño de ninguna tabla.

`assistant` habla por `WS /api/v1/assistant/ws` (protocolo en `assistant/presentation/router.py`). Escala en horizontal sin sesiones pegajosas: la conversación vive en Redis, un candado `assistant:answering:{persona}` evita dos respuestas a la vez y cada instancia mantiene **una** conexión pub/sub (`RedisHub`) que reparte los eventos a todos los sockets abiertos de la persona, estén en la instancia que estén. Sus herramientas leen siempre los datos de quien pregunta (el modelo nunca elige de quién) y el panel docente pasa por las mismas reglas de `classrooms`.

## 3. Estructura interna de cada módulo

Ejemplo: `tutoring`, la escalera de ayuda.

```
modules/tutoring/
├── domain/
│   ├── help_attempt.py                # Entidad HelpAttempt; HelpStep (HINT_1|HINT_2|STEP_BY_STEP|FINAL)
│   └── errors.py                      # StepOutOfOrder, FinalLocked, AttemptClosed
├── application/
│   ├── ports/
│   │   ├── help_attempt_repository.py # Protocol (puerto de salida)
│   │   ├── adaptation_reader.py       # Protocol: leer la adaptación (lo implementa adaptations)
│   │   └── hint_generator.py          # Protocol: generar la pista de un escalón (LLM)
│   ├── open_attempt/
│   │   ├── command.py                 # OpenAttemptCommand(person_id, adaptation_id, task_ref, class_id?)
│   │   └── handler.py                 # Caso de uso (puerto de entrada)
│   ├── request_step/
│   │   ├── command.py                 # RequestStepCommand(attempt_id, step)
│   │   └── handler.py
│   ├── submit_own_answer/             # «Inténtalo sin IA»: compara con la guía, sin LLM
│   └── get_attempt/
├── infrastructure/
│   ├── models.py                      # Tablas SQLAlchemy
│   ├── sqlalchemy_help_attempt_repository.py
│   ├── adaptation_reader_adapter.py   # Llama al caso de uso público de adaptations
│   └── llm_hint_generator.py          # Usa shared.infrastructure.llm con tope de 15 s y respaldo
└── presentation/
    ├── router.py                      # APIRouter /api/v1/help-attempts
    ├── schemas.py                     # Request y response Pydantic (contrato con el front)
    └── dependencies.py                # Wiring: Depends() que arma el handler y sus adaptadores
```

### Qué va en cada capa

| Capa | Contiene | Puede importar | Nunca importa |
| --- | --- | --- | --- |
| `domain` | Entidades, value objects, enums, reglas e invariantes, errores de dominio | `shared.domain`, stdlib | FastAPI, SQLAlchemy, Redis, Pydantic, otros módulos |
| `application` | Comandos, handlers (casos de uso), puertos `Protocol` | Su `domain`, sus `ports`, `shared.domain`, `shared.application` | `infrastructure`, FastAPI, otros módulos |
| `infrastructure` | Modelos ORM, repositorios, adaptadores a otros módulos, Redis y LLM | Su `application` y `domain`, `shared.infrastructure`, la **API pública** de otro módulo | La `presentation` de cualquier módulo |
| `presentation` | Router, esquemas, wiring de dependencias | Su `application`, su `infrastructure` (solo en `dependencies.py`), `shared.presentation` | El `domain` de otro módulo |

### API pública de un módulo

Cada módulo expone en `modules/<mod>/__init__.py` **solo** los casos de uso y DTO que otros pueden usar. Es lo único que un adaptador de otro módulo puede importar.

```python
# modules/adaptations/__init__.py
from .application.get_adaptation.handler import GetAdaptationHandler
from .application.get_adaptation.dto import AdaptationView

__all__ = ["GetAdaptationHandler", "AdaptationView"]
```

## 4. Comunicación entre módulos

El módulo que necesita algo **define el puerto con su propio vocabulario**, y un adaptador en su `infrastructure` traduce desde la API pública del otro.

```python
# modules/tutoring/application/ports/adaptation_reader.py
class AdaptationReader(Protocol):
    async def get_for_tutoring(self, adaptation_id: UUID) -> TutoringContext | None: ...


# modules/tutoring/infrastructure/adaptation_reader_adapter.py
from frobi.modules.adaptations import GetAdaptationHandler  # API pública, no su dominio


class AdaptationReaderAdapter:
    def __init__(self, get_adaptation: GetAdaptationHandler) -> None:
        self._get = get_adaptation

    async def get_for_tutoring(self, adaptation_id: UUID) -> TutoringContext | None:
        view = await self._get.handle(adaptation_id)
        return None if view is None else TutoringContext(text=view.content_text, recipe=view.recipe)
```

**Por qué:** si `adaptations` cambia su modelo interno, solo se toca el adaptador y el dominio de `tutoring` ni se entera. Es la misma idea que `attendance.CardLedger` en famas.

## 5. Piezas transversales

### Contexto de clase (privacidad, RNF16)

- `shared.presentation.deps.class_context` resuelve la membresía `joined` activa de la persona y entrega `class_id | None`.
- Todo comando que registra actividad recibe `class_id` de forma explícita, y el repositorio lo persiste.
- Los lectores del panel en `classrooms` (`ClassActivityReader`) exigen `class_id` como argumento obligatorio, sin valor por defecto. No existe una consulta del panel sin filtro de clase.

### IA (LLM)

- `shared.infrastructure.llm` tiene el cliente del proveedor, el tope `asyncio.wait_for(..., 15)`, la validación de la salida estructurada y el límite de uso en Redis.
- **No hay un puerto LLM global en `application`.** Cada módulo define su puerto con su intención (`HintGenerator`, `PromptScorer`, `ClaimReviewer`), y su adaptador usa el cliente compartido. Así los casos de uso no saben que existe un LLM.
- Cada adaptador tiene su gemelo `fallback_*.py`, con respuestas pregrabadas desde `fixtures/`, y su `fake_*.py` determinista para los tests.

### Unit of Work y transacciones

- `shared.application.UnitOfWork` es el puerto y `SqlAlchemyUnitOfWork` el adaptador.
- Un handler, una transacción. Los casos con carrera (doble clic en «Adaptar», abrir un escalón dos veces) se resuelven con un bloqueo en Redis y una restricción en la BD como red final.

### Errores

- Los errores de dominio son clases con un `code` estable, por ejemplo `Tutoring.FinalLocked` o `Tutoring.StepOutOfOrder`.
- `shared.presentation` los mapea a `application/problem+json` con su status HTTP. El front muestra el texto y el ícono según `code` (RF31).

| Error | HTTP | Código |
| --- | --- | --- |
| Validación de entrada | 422 | `Validation.Invalid` |
| Código de clase inválido | 422 | `Classrooms.InvalidCode` |
| PDF ilegible | 422 | `Materials.PdfUnreadable` |
| Escalón fuera de orden | 409 | `Tutoring.StepOutOfOrder` |
| Respuesta final bloqueada | 409 | `Tutoring.FinalLocked` |
| Sin sesión | 401 | `Identity.Unauthenticated` |
| Rol insuficiente | 403 | `Identity.Forbidden` |

## 6. Reglas de dependencia (import-linter)

Se verifican en CI, como en famas. Si falla una regla, el pipeline se rompe.

```toml
[tool.importlinter]
root_package = "frobi"

[[tool.importlinter.contracts]]
name = "Hexagonal layers inside each module"
type = "layers"
layers = ["presentation", "infrastructure", "application", "domain"]
containers = [
  "frobi.modules.identity", "frobi.modules.onboarding", "frobi.modules.settings",
  "frobi.modules.materials", "frobi.modules.adaptations", "frobi.modules.tutoring",
  "frobi.modules.prompt_coach", "frobi.modules.comprehension", "frobi.modules.claim_review",
  "frobi.modules.tools", "frobi.modules.classrooms", "frobi.modules.progress",
]

[[tool.importlinter.contracts]]
name = "Domain and application stay framework-free"
type = "forbidden"
source_modules = ["frobi.modules.*.domain", "frobi.modules.*.application"]
forbidden_modules = ["fastapi", "sqlalchemy", "redis", "pydantic"]

[[tool.importlinter.contracts]]
name = "No module reaches into another module's internals"
type = "forbidden"
source_modules = ["frobi.modules.*.domain", "frobi.modules.*.application"]
forbidden_modules = ["frobi.modules"]
ignore_imports = ["frobi.modules.** -> frobi.shared.**"]
allow_indirect_imports = true
```

> El tercer contrato es el punto de partida. Al montar el repo hay que ajustarlo para permitir los imports dentro del propio módulo; la sintaxis exacta se valida con `lint-imports` en la Fase 0.

Resumen de las reglas:

- `domain` no importa nada fuera de `shared.domain`.
- `application` importa su `domain` y sus propios `ports`; nunca `infrastructure` ni FastAPI.
- `presentation` e `infrastructure` dependen hacia adentro.
- Un módulo **no importa el dominio de otro**: usa un puerto propio y un adaptador sobre la API pública del otro (`__init__.py`).
- `shared` no importa nada de `modules`.

## 7. Tests por capa

| Carpeta | Qué prueba | Dobles |
| --- | --- | --- |
| `tests/unit/<modulo>/domain` | Invariantes: orden de la escalera, puntaje de 0 a 4, autonomía de 1 a 3 | Ninguno |
| `tests/unit/<modulo>/application` | Handlers | Fakes en memoria de cada puerto |
| `tests/integration` | Repositorios SQLAlchemy, Redis y filtros por `class_id` | Postgres y Redis reales (testcontainers) |
| `tests/e2e` | Contrato HTTP completo, códigos de error y respaldo de la IA | `fake_*` del LLM; nunca el proveedor real |

TDD estricto: cada caso de uso nace con su test rojo en `unit/`.

## 8. Receta para agregar un caso de uso

1. Escribir el test del dominio o del handler en `tests/unit/<modulo>/` y verificar que falla.
2. Agregar o ajustar la regla en `domain/`.
3. Crear `application/<caso_de_uso>/command.py` y `handler.py`. Si se necesita algo externo, definir el puerto en `application/ports/`.
4. Implementar el adaptador en `infrastructure/` y su test de integración si toca la BD o Redis.
5. Exponer el endpoint en `presentation/router.py`, su esquema en `schemas.py` y el wiring en `dependencies.py`.
6. Correr `ruff`, `mypy`, `lint-imports` y `pytest`, y actualizar el snapshot de `openapi.json` si cambió el contrato.
