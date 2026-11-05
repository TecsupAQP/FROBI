# FROBI · Interfaces (maqueta)

Maqueta navegable de FROBI (Hack4Edu Arequipa 2026). Solo interfaces: todos los datos son mock.
Fuente de verdad del diseño: Figma «FROBI», página «Diseño v2 · Brief».

## Arranque

```bash
npm install
npm run dev        # http://localhost:5173
npm run build      # vue-tsc + vite build
npm run lint
```

Node 16+ (Vite 4).

## Rutas

| Ruta | Pantalla (Figma) |
| --- | --- |
| `/login` | 2 · Login |
| `/` | 3 · V1 Inicio + 4 · Modal de subida |
| `/guia` | 5 · V2 Guía y formatos |
| `/resultado/:formato` | 6 · V3 Resultado (`mapa-visual`, `ejemplo-real`, `lectura-facil`, `audio`) |
| `/verificacion` | 7 · V3 Verificación |
| `/pidelo-tu` | 8 · V4 Pídelo tú |
| `/progreso` | 9 · V5 Mi progreso |
| `/docente` | 10 · V6 Panel docente |
| `/trae-tu-trabajo` | 14 · Trae tu trabajo |
| `/revision` | 15 · Revisión de afirmaciones |
| `/herramientas` | 16 · Herramientas recomendadas |
| `/cierre` | 12 · Cierre del recorrido |

Si se entra directo a una ruta sin pasar por el login, se usa el estudiante de ejemplo `mecatronico_01`.

## Estados simulados (Figma · 11 y 13)

Añade `?estado=` a cualquier URL:

| Valor | Efecto |
| --- | --- |
| `cargando` | Las peticiones mock no terminan nunca |
| `vacio` | Mi progreso sin datos |
| `error-respaldo` | V3 muestra la versión guardada; la subida de PDF falla («No pudimos leer este PDF») |
| `sin-conexion` | Las peticiones fallan con error de conexión |

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
  core/<dominio>/       application/use-case (mock) · infraestructure/ports · adapters/in/service
  core/shared/domain/   tipos: Student, Material, Adaptation, PromptScore, ClaimReview, Tool…
  mocks/                datos de ejemplo tipados
  router/ enums/ constants/ views/
```

Cada componente y vista es una carpeta con tres archivos, igual que en la referencia:

- `cmp-x.vue`: solo la plantilla, con `<script src="./cmp-x.ts" lang="ts">` y `<style src="./cmp-x.scss" lang="scss" scoped>`.
- `cmp-x.ts`: `defineComponent({ components, props, emits, setup() })`. El `setup` llama al composable y devuelve lo que usa la plantilla. Los eventos se emiten con `$emit` en la plantilla y el `v-model` usa `useModel`.
- `cmp-x.scss`: estilos BEM con `$prefix`.

Para conectar el backend solo se reemplaza cada `*.use-case.ts`: vistas, stores y servicios no cambian.

Los iconos se regeneran con `node scripts/generar-iconos.mjs` a partir de los SVG de `assets/resources/icons`.
