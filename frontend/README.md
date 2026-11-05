# FROBI · Frontend

Front de FROBI (Hack4Edu Arequipa 2026), conectado a la API de [`../backend`](../backend).
Fuente de verdad del diseño: Figma «FROBI», página «Diseño v2 · Brief».

## Arranque

1. Levanta la API (desde la raíz del repo):

   ```bash
   cd backend
   docker compose -f docker/compose.yml up -d --build   # api :8000, postgres, redis
   ```

2. Levanta el front:

   ```bash
   cd frontend
   npm ci
   npm run dev        # http://localhost:5173 (es el origen que permite el CORS de la API)
   ```

Otros comandos: `npm run build` (vue-tsc + vite build), `npm run type-check`, `npm run lint`.
Node 16+ (Vite 4).

La URL de la API se cambia con `VITE_API_URL` (ver [`.env.example`](./.env.example)); por defecto es
`http://localhost:8000/api/v1`.

## Cómo entrar

- `/login`: alias, carrera y rol. Sin correo ni contraseña (`POST /sessions`).
- **Código de clase (opcional):** el que genera la API al crear una clase (Crear clase → Invitar), o
  `SENSOR1`, la clase de ejemplo que trae la base. Un código que no existe muestra «No encontramos esa
  clase» y no deja entrar.
- El token se guarda en `localStorage` (`frobi-token`). Si la API responde 401, el front vuelve a `/login`
  y, al entrar, regresa a la pantalla donde estabas.
- Sin sesión solo se ven `/login`, `/como-se-usa` y `/demo/personas`.

## Rutas

| Ruta | Pantalla (Figma) |
| --- | --- |
| `/login` | 2 · Login |
| `/rol`, `/intro`, `/asistente/:paso`, `/perfil-accesibilidad` | 17 y 22 · Rol, introducción y primera configuración |
| `/` | 3 · V1 Inicio + 4 · Subir PDF |
| `/guia` | 5 · V2 Guía y formatos |
| `/resultado/:formato` | 6 · V3 Resultado (`mapa-visual`, `ejemplo-real`, `lectura-facil`, `audio`) |
| `/guia/:tarea/ayuda`, `/guia/:tarea/sin-ia` | 20 · Escalera de ayuda e «Inténtalo sin IA» (tarea `sensor-vidrio`) |
| `/verificacion` | 7 · V3 Verificación |
| `/pidelo-tu` | 8 · V4 Pídelo tú |
| `/progreso`, `/cierre` | 9 y 12 · Mi progreso y cierre |
| `/trae-tu-trabajo`, `/revision`, `/herramientas` | 14, 15 y 16 · Trabajo, afirmaciones y herramientas |
| `/docente`, `/docente/clase/nueva`, `/docente/clase/invitar`, `/docente/alumno/:alias` | 10, 18 y 19 · Docente |
| `/ajustes` | 24 · Ajustes |
| `/como-se-usa`, `/demo/personas` | 21 y 23 · Presentación (datos de ejemplo a propósito) |

## Qué endpoint usa cada pantalla

| Dominio (`src/core/…`) | Endpoints |
| --- | --- |
| `autenticacion` | `POST /sessions`, `DELETE /sessions/current`, `PATCH /me` |
| `perfil` | `GET /me`, `POST /me/onboarding` (`/reset`), `GET`/`PATCH /me/settings`, `GET /languages`, `POST /classes/join` |
| `material` | `GET /materials/guides` (Mis guías), `GET /materials/samples`, `GET /materials/{id}`, `POST /materials/upload`, `POST /materials` |
| `adaptacion` | `POST /materials/{id}/adaptations` |
| `ayuda` | `POST /help-attempts`, `POST /help-attempts/{id}/steps`, `POST /help-attempts/{id}/own-answer` |
| `verificacion` | `POST /adaptations/{id}/questions`, `POST /questions/{id}/answers` |
| `entrenador` | `POST /prompt-evaluations`, `POST /prompt-evaluations/{id}/compare`, `GET /me/journey-summary` |
| `trabajo` | `POST /materials` (consigna y borrador), `POST /works`, `POST /works/{id}/claim-review` |
| `herramientas` | `GET /tools`, `POST /tools/recommendations` |
| `progreso`, `cierre` | `GET /me/progress`, `GET /me/journey-summary` |
| `clase`, `docente` | `POST /classes`, `GET /classes/{id}`, `/members`, `/dashboard`, `/students/{id}`, `POST /classes/{id}/invitations` y `/materials`, `DELETE /me/membership` |

Notas del contrato:

- La API habla en inglés (`visual_map`, `hint_1`, `supported`…); `core/shared/infraestructure/http/api.mapper.ts`
  lo traduce al vocabulario del front.
- La escalera y las preguntas se piden sobre una adaptación: el front recuerda el material y la última
  adaptación vistos (`contexto-estudio.ts`). Si aún no hay ninguna, pide una en lectura fácil.
- La escalera no abre nada sola (RF39): cada escalón se pide con su botón y la API exige el orden
  pista 1 → pista 2 → paso a paso → respuesta final (esta, además, después de un intento propio).
- «Inténtalo sin IA» abre su propio intento: practicar sin IA cuenta como logro aunque antes se hayan
  pedido pistas en la escalera.
- Lo que la API no guarda vive en el navegador: por qué puerta entró la persona (`frobi-perfil-local`) y la
  clase que creó el docente (`frobi-clase-id`).
- El audio lo lee la voz del navegador (Web Speech API); la API entrega el texto.

## Arquitectura

Sigue las convenciones del proyecto de referencia (`erp-mf-configuracion`), con Pinia en lugar de Vuex:

```
src/
  assets/styles/        _variables (tokens) · _tokens (custom properties) · _mixin (tablet/escritorio) · _reset
  assets/resources/     iconos e imágenes descargados de Figma
  components/base/      v-*   (botón, campo, select, radio, chips y tarjetas de pieza, modal, semáforo…)
  components/common/    cmp-* de layout (barra superior, layout de página, encabezado, avisos)
  components/business/  cmp-* por pantalla, con content/ y modals/
  composables/          envuelven cada store (los componentes no leen el store directamente)
  store/                stores Pinia en estilo setup
  core/<dominio>/       application/use-case (llama a la API) · infraestructure/ports · adapters/in/service
  core/shared/          domain/view (tipos del front) · infraestructure/http (cliente, DTO de la API, traducciones)
  constants/            catálogos fijos del front (carreras, tareas, plantilla de instrucción…)
  mocks/                solo los datos de ejemplo de las pantallas de presentación (21 y 23)
  router/ enums/ views/
```

Cada componente y vista es una carpeta con tres archivos, igual que en la referencia:

- `cmp-x.vue`: solo la plantilla, con `<script src="./cmp-x.ts" lang="ts">` y `<style src="./cmp-x.scss" lang="scss" scoped>`.
- `cmp-x.ts`: `defineComponent({ components, props, emits, setup() })`. El `setup` llama al composable y devuelve lo que usa la plantilla. Los eventos se emiten con `$emit` en la plantilla y el `v-model` usa `useModel`.
- `cmp-x.scss`: estilos BEM con `$prefix`.

Cada `*.use-case.ts` es la única pieza que conoce la API: si cambia el contrato, se ajusta ahí y en
`api.dto.ts`; vistas, stores y servicios no cambian.

Los iconos se regeneran con `node scripts/generar-iconos.mjs` a partir de los SVG de `assets/resources/icons`.
