# FROBI · Plan del backend

> Fuente: «FROBI · Requerimientos completos (v3)», del 4 de noviembre de 2026.
> Stack: **FastAPI · PostgreSQL · Redis**. Alcance: solo el backend.
> Fecha límite: **final de Hack4Edu, 7 de noviembre de 2026**. Quedan unos 3 días.

## 1. Objetivo y estrategia

El front ya existe con datos simulados, así que el backend tiene que reemplazar esos mocks sin bloquearlo. La estrategia es **contrato primero**:

1. **Fase 0:** el repo y el contrato OpenAPI, con endpoints que devuelven datos de ejemplo. El front se conecta desde el primer día.
2. **Fases 1 a 3:** se reemplazan los stubs por lógica real, por prioridad MoSCoW (Debe → Debería → Podría).

Regla de oro: **el contrato no cambia de forma sin avisar al front**. Si un campo cambia, se versiona o se agrega; no se rompe.

## 2. Stack y decisiones técnicas

| Pieza | Elección | Por qué |
| --- | --- | --- |
| Lenguaje y paquetes | Python 3.12 + `uv` | Instalación rápida y lockfile reproducible |
| API | FastAPI + Pydantic v2 | El OpenAPI se genera solo y sirve de contrato con el front |
| ORM y migraciones | SQLAlchemy 2.0 (async) + `asyncpg` + Alembic | Estándar, asíncrono y con migraciones versionadas |
| Base de datos | PostgreSQL 16 | Fuente de verdad de personas, clases, materiales y actividad |
| Caché y efímeros | Redis 7 | Sesiones, caché de adaptaciones, límite de uso de la IA y bloqueos |
| PDF | `pypdf` | Extracción de texto liviana (RF02) |
| IA | Puertos por módulo + cliente LLM compartido | El proveedor sigue pendiente; se arranca con adaptadores `fake` y de respaldo |
| Tests | `pytest` + `pytest-asyncio` + `httpx` + testcontainers | TDD estricto, con Postgres y Redis reales en integración |
| Calidad | `ruff` + `mypy` | Lint, formato y tipos en CI |
| Infraestructura local | `docker compose` (api, postgres, redis) | Un comando para levantar todo |
| CI | GitHub Actions: lint, tipos, tests y exportación de `openapi.json` | RNF09: repo público con licencia libre |

### Decisiones clave

- **Autenticación sin contraseña (RF28, RNF08).** `POST /sessions` con alias, carrera y rol devuelve un token opaco. Redis guarda `session:{token} → person_id` con TTL de 30 días. No se piden datos personales.
- **Rol docente sin verificación.** En la demo, quien elige «Docente» lo es. Es un riesgo conocido y aceptado en la hackatón; queda documentado.
- **Contexto de clase en cada actividad (RNF16, RF49, RF53).** Toda fila de actividad (adaptación, intento de ayuda, respuesta, instrucción) guarda un `class_id`, que es `NULL` fuera de una clase. El panel docente filtra siempre por `class_id = :clase`. Así, lo hecho fuera de la clase **no se puede** filtrar al docente, por diseño y no por disciplina.
- **Tope de 15 s para la IA (RF04, RF29, RNF03).** Cada llamada pasa por `asyncio.wait_for(..., 15)`. Si hay timeout o error, se usa el adaptador de respaldo con respuestas pregrabadas de la guía de sensores y la respuesta lleva `fallback: true`.
- **Clave de la IA solo en el servidor (RNF07).** Se lee desde la variable de entorno y nunca se devuelve.
- **Vocabulario controlado (RNF11, RNF14).** Los estados de las afirmaciones son un enum cerrado: `supported`, `unverifiable` y `contradicts`. No existe «falso» ni un porcentaje de IA en ningún esquema.
- **Errores uniformes (RF31).** Se responde con `application/problem+json` (RFC 9457), con `code` estable para que el front muestre el texto y el ícono adecuados.

## 3. Arquitectura

Monolito modular hexagonal, con la misma convención que `famas`. El detalle está en [`ARCHITECTURE.md`](./ARCHITECTURE.md): estructura de `src/frobi/modules/<modulo>/{domain,application,infrastructure,presentation}`, una carpeta por caso de uso, comunicación entre módulos por puertos y reglas verificadas con `import-linter`.

## 4. Modelo de datos (PostgreSQL)

| Tabla | Campos principales | Notas |
| --- | --- | --- |
| `persons` | id (uuid), alias, career, role (`learner`/`teacher`), configured_by (`self`/`companion`), created_at | Sin email ni contraseña |
| `person_settings` | person_id (PK), profiles (text[]), voice, high_contrast, large_text, short_texts, captions, large_buttons, keyboard_mode, language, intro_status (`seen`/`skipped`/`pending`), onboarding_done | 1:1 con `persons` |
| `classes` | id, name, subject, teacher_id, invite_code (único), tasks (jsonb), created_at | |
| `memberships` | id, person_id, class_id, status (`invited`/`joined`/`left`), invited_alias, joined_at, left_at | Un único `joined` activo por persona |
| `materials` | id, owner_id, class_id?, title, kind (`guide`/`brief`/`draft`/`class_content`), source (`sample`/`upload`/`paste`), extracted_text, created_at | |
| `works` | id, person_id, class_id?, brief_material_id, draft_material_id, organized (jsonb) | Consigna y borrador (RF18) |
| `adaptations` | id, material_id, person_id, class_id?, format (`visual_map`/`real_example`/`easy_read`/`audio`), content (jsonb), recipe (jsonb: context, goal, level, format), fallback (bool), created_at | |
| `help_attempts` | id, person_id, class_id?, adaptation_id, task_ref, max_step (`none`/`hint_1`/`hint_2`/`step_by_step`/`final`), own_answer, self_check (jsonb), solved_without_ai (bool), created_at | |
| `prompt_evaluations` | id, person_id, class_id?, text, scores (jsonb: 4 piezas de 0 a 4), suggestion, improved_text, autonomy_level (1 a 3), context_ref | |
| `questions` | id, adaptation_id, kind (`comprehension`/`transfer`), statement, options (jsonb), correct_option, feedback (jsonb) | |
| `answers` | id, question_id, person_id, class_id?, chosen_option, is_correct, used_help (bool), created_at | |
| `claims` | id, work_id, section, fragment, status (`supported`/`unverifiable`/`contradicts`), reason, backing_passage? | |
| `tools` | id, name, need, use_for, avoid_for | Seed fijo de 5 (RF22) |

**Índices:** `memberships(class_id, status)`, `invite_code` único, y `(class_id, person_id)` en cada tabla de actividad para el panel docente.

## 5. Uso de Redis

| Clave | Contenido | TTL |
| --- | --- | --- |
| `session:{token}` | person_id | 30 días |
| `adapt:{sha256(texto+formato+perfiles)}` | Adaptación generada | 24 h; evita pagar dos veces la misma llamada (RF05) |
| `ratelimit:ai:{person_id}` | Contador | 60 s; protege la cuota del proveedor |
| `lock:adapt:{hash}` | Bloqueo | 20 s; evita generar lo mismo en paralelo por doble clic |
| `dashboard:{class_id}` | Resumen del panel | 60 s; se invalida cuando hay actividad nueva en la clase |

## 6. Endpoints

Prefijo: `/api/v1`. Autenticación: `Authorization: Bearer <token>`, salvo donde se indica.
Prioridad: **D** = Debe · **Db** = Debería · **P** = Podría.

### Transversal

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| GET | `/health` | Estado de la API, Postgres y Redis (sin auth) | — | D |
| GET | `/openapi.json` | Contrato para el front (sin auth) | — | D |

### M1 · Cuenta y acceso

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| POST | `/sessions` | Entrar con `{alias, career, role, class_code?}` y recibir `{token, person, membership?}`. Un código inválido da 422 con `code: invalid_class_code` y no bloquea la entrada sin clase | RF28, RF32, RF33 | D |
| DELETE | `/sessions/current` | Cerrar la sesión | — | D |
| GET | `/me` | Persona actual, clase activa y estado del asistente | RF32 | D |

### M2 · Primera configuración

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| GET | `/accessibility-profiles` | Catálogo de perfiles y los ajustes que activa cada uno | RF35 | D |
| POST | `/me/onboarding` | `{who_uses: self\|companion, profiles[], intro: seen\|skipped}`; aplica los ajustes de los perfiles | RF34, RF35, RF36, RF37 | D |
| POST | `/me/onboarding/skip` | Omitir el asistente | RF34 | D |
| POST | `/me/onboarding/reset` | «Volver a hacer el asistente» | RF38 | Db |

### M3 · Material

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| GET | `/materials/samples` | Guías de ejemplo (sensores industriales) | RF01 | D |
| POST | `/materials` | Pegar texto: `{title, kind, text}` | RF02 | D |
| POST | `/materials/upload` | PDF por multipart (máximo 10 MB). Devuelve el texto extraído para la vista previa; un PDF ilegible da 422 `pdf_unreadable` | RF02, RF31 | D |
| GET | `/materials/{id}` | Detalle y texto extraído | RF01 | D |
| POST | `/works` | `{brief, draft}`: organiza requisitos y temas sin juzgar la autoría | RF18 | D |

### M4 y M5 · Adaptación, receta y límites

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| GET | `/formats` | Los 4 formatos con ícono, descripción y el sugerido según el perfil | RF03, RF35 | D |
| POST | `/materials/{id}/adaptations` | `{format}` → `{content, recipe{context, goal, level, format}, prompt_text, ai_notice, fallback}`. Tope de 15 s con respaldo | RF04, RF05, RF07, RF29, RF30 | D |
| GET | `/adaptations/{id}` | Volver a ver una adaptación. En audio se devuelve texto: la voz es del navegador (RF06) | RF05, RF06 | D |

> «Copiar receta» (RF08) lo resuelve el front con `prompt_text`. No necesita endpoint.

### M6 · Tutor con escalera de ayuda

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| POST | `/help-attempts` | Abrir un intento sobre una tarea o adaptación `{adaptation_id, task_ref}` | RF39 | D |
| POST | `/help-attempts/{id}/steps` | `{step}`: abre **solo el siguiente** escalón. Un salto da 409 `step_out_of_order`; pedir `final` sin intento propio da 409 `final_locked` («Se desbloquea después de tu intento») | RF39, RF40 | D |
| POST | `/help-attempts/{id}/own-answer` | `{answer, self_check[]}`: «Inténtalo sin IA». Compara con los pasajes de la guía **sin IA** (búsqueda de texto) y marca `solved_without_ai` | RF41, RF42 | D |
| GET | `/help-attempts/{id}` | Estado: escalón actual y nivel de ayuda («Nivel 2, con pistas») | RF43 | Db |

### M7 · Entrenador de instrucciones

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| POST | `/prompt-evaluations` | `{text, material_id?, claim_id?}` → puntaje de 0 a 4 por pieza, primero la pieza que falta, sugerencia, versión mejorada y nivel de autonomía | RF09, RF10, RF12, RF23 | D |
| POST | `/prompt-evaluations/{id}/compare` | Corre la original y la mejorada; resultados lado a lado | RF11 | D |

### M8 · Verificación

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| POST | `/adaptations/{id}/questions` | Genera 2 o 3 preguntas de opción múltiple basadas en el material | RF13 | D |
| POST | `/questions/{id}/answers` | `{option}` → acierto, retroalimentación y, si falla, `suggested_format` («Prueba con…») | RF13, RF14 | D |
| POST | `/adaptations/{id}/transfer-question` | Pregunta similar sin ayuda; se registra con `used_help: false` | RF24 | Db |

### M9 · Revisión de afirmaciones

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| POST | `/works/{id}/claim-review` | Lista por sección: estado, motivo, fragmento y respaldo. Si no hay respaldo, devuelve «No hay respaldo en tu material». En la demo corre sobre un caso guionado | RF19, RF20 | D |
| GET | `/works/{id}/claims` | Volver a ver la revisión | RF19 | D |

### M10 · Herramientas recomendadas

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| POST | `/tools/recommendations` | `{need?, claim_id?}` → herramienta, por qué sirve y cuándo no usarla | RF21 | D |
| GET | `/tools?need=` | Catálogo fijo de 5, filtrable | RF22 | P |

### M11 · Progreso y cierre

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| GET | `/me/progress` | Formatos usados, aciertos por formato, evolución del puntaje, «Resuelto sin IA» y mensaje en palabras. Si no hay datos, devuelve un estado vacío explícito | RF15, RF16, RF42, RF31 | Db |
| GET | `/me/journey-summary` | Cierre: formato, receta aprendida, puntaje y autonomía | RF27 | Db |

### M12 · Clase del docente (capa extra; solo rol `teacher`)

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| POST | `/classes` | `{name, subject, tasks[]}` → clase y `invite_code` | RF44 | Db |
| GET | `/classes/{id}` | Detalle de la clase | RF44 | Db |
| POST | `/classes/{id}/materials` | Subir contenido (texto o PDF) con `kind=class_content` | RF45 | Db |
| POST | `/classes/{id}/invitations` | `{aliases[]}` → invitaciones pendientes | RF46 | Db |
| GET | `/classes/{id}/members` | Código y lista con estado («Se unió», «Invitación pendiente») | RF46 | Db |
| POST | `/classes/join` | Estudiante: `{code}` para unirse después de entrar | RF33 | Db |
| GET | `/classes/{id}/dashboard` | Avance y alertas por alumno con texto e ícono, formatos más pedidos, preguntas más falladas y uso de IA. Lleva `sample_data: true` mientras no haya datos reales | RF17, RF25, RF47, RNF12 | Db |
| GET | `/classes/{id}/students/{person_id}` | Alias, formato preferido, aciertos, ayudas por escalón, lo resuelto sin IA y la pregunta más fallada. **Solo actividad con ese `class_id`** | RF26, RF48 | P |

### M13 · Ajustes y privacidad

| Método | Ruta | Descripción | RF | Prio |
| --- | --- | --- | --- | --- |
| GET | `/me/settings` | Ajustes actuales | RF51 | Db |
| PATCH | `/me/settings` | Interruptores de accesibilidad e idioma | RF50, RF51 | Db |
| PATCH | `/me` | Cambiar el alias | RF52 | Db |
| DELETE | `/me/membership` | «Salir de la clase»; la actividad posterior queda con `class_id = NULL` | RF49 | Db |
| GET | `/me/privacy` | «Qué ve tu docente»: qué categorías se comparten dentro de la clase y cuáles no | RF53 | Db |
| GET | `/languages` | `es` disponible; `qu` y `ay` como `coming_soon` | RF50 | P |

### Fuera del backend

| RF | Motivo |
| --- | --- |
| RF06 (voz) | Lo hace la Web Speech API del navegador; el backend solo entrega el texto |
| RF08 (copiar) | Portapapeles del navegador |
| RF54 (recorrido de 9 pasos) | Pantalla estática con datos de ejemplo en el front |

## 7. Motor de IA (puertos)

Cada módulo define su propio puerto según su intención, y sus adaptadores usan el cliente compartido `shared.infrastructure.llm` (ver [`ARCHITECTURE.md`](./ARCHITECTURE.md) §5).

| Módulo | Puerto | Método |
| --- | --- | --- |
| `adaptations` | `TextGenerator` | `adapt(text, fmt, profile) -> AdaptationDraft` |
| `tutoring` | `HintGenerator` | `hint(context, step) -> str` |
| `prompt_coach` | `PromptScorer` | `score(prompt, context) -> PromptScore` |
| `comprehension` | `QuestionGenerator` | `generate(text, n) -> list[QuestionDraft]` |
| `claim_review` | `ClaimReviewer` | `review(draft, material) -> list[ClaimDraft]` |

- **Prompts versionados** en `shared/infrastructure/llm/prompts/`. La receta de 4 piezas que se muestra (RF07) es **la misma** que se envía al modelo; se arma en un solo lugar.
- **Instrucción de sistema fija:** usar solo el material cargado y avisar si algo no está ahí (regla del motor).
- **Salida estructurada** validada con Pydantic. Si la respuesta es inválida, se cuenta como fallo y se usa el respaldo.
- **Proveedor:** pendiente (decisión abierta del documento). El puerto permite cambiarlo sin tocar los casos de uso.

## 8. Fases de trabajo

### Fase 0 · Repo y contrato para el front (4 de noviembre)

- [x] `git init` propio en `forbi/`. Hoy `~` es un repo git; hay que evitar que `forbi` quede dentro.
- [ ] Repo en GitHub con licencia libre (RNF09); nombre y visibilidad por confirmar.
- [x] `pyproject.toml` (uv), `ruff`, `mypy`, `pytest` y `docker-compose.yml` con api, postgres y redis.
- [x] App factory, `/health`, problem+json y CORS para el origen del front.
- [x] **Todos los esquemas Pydantic de la sección 6** y routers stub que devuelven fixtures de ejemplo.
- [x] `openapi.json` exportado en CI y publicado en el repo. **Es lo que se le entrega al front.**
- [x] README con cómo levantarlo (`docker compose up`) y cómo autenticarse.

### Fase 1 · Núcleo «Debe» (5 de noviembre)

Orden según el flujo de la demo; cada paso en TDD (rojo, verde, refactor):

1. [ ] M1: sesiones con alias y token en Redis, `current_person`, código de clase opcional.
2. [ ] M2: onboarding, perfiles y ajustes derivados.
3. [ ] M3: samples (seed de la guía de sensores), pegado de texto, PDF con `pypdf`, `works`.
4. [ ] Puerto de IA con adaptadores `Fake` y `Fallback`, y tope de 15 s.
5. [ ] M4 y M5: adaptaciones con receta, aviso, caché y bloqueo en Redis.
6. [ ] M6: máquina de estados de la escalera, con reglas de dominio puras y tests unitarios exhaustivos.
7. [ ] M7: evaluación de las 4 piezas y comparación.
8. [ ] M8: preguntas y respuestas con formato sugerido.
9. [ ] M9: revisión de afirmaciones con caso guionado.
10. [ ] M10: recomendación sobre el catálogo fijo.
11. [ ] Conectar el proveedor real de IA (si ya se decidió) detrás del puerto.

### Fase 2 · «Debería» (6 de noviembre)

- [ ] M11: progreso y cierre.
- [ ] M12: clases, invitaciones, unirse, panel con alertas y caché del panel.
- [ ] M13: ajustes, cambio de alias, salir de la clase y «Qué ve tu docente».
- [ ] RF14, RF24 y RF43.
- [ ] **Test de privacidad (RNF16):** la actividad de un alumno fuera de la clase nunca aparece en el panel ni en el detalle.

### Fase 3 · «Podría» y cierre (7 de noviembre, mañana)

- [ ] RF22 (catálogo filtrable), RF26 y RF48 (detalle del alumno) y RF50 (idiomas).
- [ ] Seed de demo: un docente, 2 alumnos y actividad marcada como `sample_data` (RF54, RNF12).
- [ ] Prueba completa de la demo contra el front y congelamiento del contrato.

## 9. Estrategia de tests (TDD estricto)

| Nivel | Qué cubre | Ejemplos críticos |
| --- | --- | --- |
| Unit (dominio) | Reglas puras, sin I/O | Escalera: no saltar escalones; `final` bloqueado sin intento. Puntaje de 0 a 4 por pieza. Autonomía de 1 a 3. Enum de afirmaciones sin «falso» |
| Integración | Repositorios con Postgres y Redis reales (testcontainers) | Unicidad de `invite_code`. Filtro por `class_id`. TTL de sesión |
| API | Contrato HTTP con `httpx.AsyncClient` | 401 sin token. 403 si un alumno pide el panel. 409 `final_locked`. Respaldo cuando la IA tarda más de 15 s (con `Fake` lento) |
| Contrato | El snapshot de `openapi.json` no cambia sin aprobación | Falla en CI si se rompe la forma de una respuesta |

La IA **nunca** se llama en los tests: se usa el adaptador `Fake`, que es determinista.

## 10. Trazabilidad de los RNF

| RNF | Cómo lo cumple el backend |
| --- | --- |
| RNF01 | Entrar, elegir el sample y adaptar: 3 llamadas, sin clase |
| RNF03 y RNF06 | `wait_for(15)` y adaptador de respaldo con la guía de sensores |
| RNF07 | Clave solo en una variable de entorno del servidor; `.env` en `.gitignore` |
| RNF08 | Sin email ni contraseña; los materiales solo se usan para la persona que los subió |
| RNF09 | Repo público, licencia MIT y CI |
| RNF10 | `language` en los ajustes; textos del servidor en catálogos por idioma |
| RNF11 y RNF14 | Enum cerrado de estados; ningún campo de «% IA» |
| RNF12 y RNF18 | Flag `sample_data` en el panel y en los seeds |
| RNF16 | `class_id` en cada actividad y filtro obligatorio en los repositorios del panel |
| RNF17 | Textos de alerta en catálogo, redactados como ayuda («Se traba en la pista 1») |

## 11. Riesgos y decisiones abiertas para el backend

- [ ] **Proveedor de IA:** sin él, la demo corre con `Fallback`. Hay que decidirlo antes del 5 de noviembre al mediodía.
- [ ] **Nombre y visibilidad del repo** en GitHub.
- [ ] **Umbrales de las alertas** del panel: «propuesta por validar» según el documento. Se dejan configurables.
- [ ] **Verificación externa frente al catálogo fijo** (M9): por ahora solo el material subido es la fuente de verdad.
- [ ] **Rol docente sin verificación:** aceptable en la hackatón; no en producción.
- [ ] **Origen del front para CORS:** URL de desarrollo y de la demo.
