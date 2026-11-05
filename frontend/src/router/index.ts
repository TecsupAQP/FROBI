import { createRouter, createWebHistory, type RouteRecordRaw } from "vue-router";
import { RutaEnum, SeccionNavEnum } from "@/enums/ruta.enum";
import { esFormatoValido } from "@/constants/formatos.constant";
import { useCmpSesionStore } from "@/store/common/cmp-sesion/cmp-sesion.store";
import { registrarAlPerderSesion } from "@/core/shared/infraestructure/http/api.client";

declare module "vue-router" {
  interface RouteMeta {
    titulo: string;
    seccion?: SeccionNavEnum;
  }
}

const routes: RouteRecordRaw[] = [
  {
    path: "/login",
    name: RutaEnum.LOGIN,
    component: () => import("@/views/vw-login/vw-login.vue"),
    meta: { titulo: "Entrar" },
  },
  {
    path: "/",
    name: RutaEnum.INICIO,
    component: () => import("@/views/vw-inicio/vw-inicio.vue"),
    meta: { titulo: "Inicio", seccion: SeccionNavEnum.INICIO },
  },
  {
    path: "/guia",
    name: RutaEnum.GUIA,
    component: () => import("@/views/vw-guia/vw-guia.vue"),
    meta: { titulo: "Guía y formatos", seccion: SeccionNavEnum.GUIA },
  },
  {
    path: "/resultado/:formato",
    name: RutaEnum.RESULTADO,
    component: () => import("@/views/vw-resultado/vw-resultado.vue"),
    meta: { titulo: "Resultado", seccion: SeccionNavEnum.GUIA },
    beforeEnter: (to) =>
      esFormatoValido(to.params.formato)
        ? true
        : { name: RutaEnum.RESULTADO, params: { formato: "mapa-visual" } },
  },
  {
    path: "/verificacion",
    name: RutaEnum.VERIFICACION,
    component: () => import("@/views/vw-verificacion/vw-verificacion.vue"),
    meta: { titulo: "Verificación", seccion: SeccionNavEnum.GUIA },
  },
  {
    path: "/pidelo-tu",
    name: RutaEnum.PIDELO_TU,
    component: () => import("@/views/vw-pidelo-tu/vw-pidelo-tu.vue"),
    meta: { titulo: "Pídelo tú", seccion: SeccionNavEnum.GUIA },
  },
  {
    path: "/progreso",
    name: RutaEnum.PROGRESO,
    component: () => import("@/views/vw-progreso/vw-progreso.vue"),
    meta: { titulo: "Mi progreso", seccion: SeccionNavEnum.PROGRESO },
  },
  {
    path: "/docente",
    name: RutaEnum.DOCENTE,
    component: () => import("@/views/vw-docente/vw-docente.vue"),
    meta: { titulo: "Panel docente", seccion: SeccionNavEnum.DOCENTE },
  },
  {
    path: "/trae-tu-trabajo",
    name: RutaEnum.TRAE_TU_TRABAJO,
    component: () => import("@/views/vw-trae-tu-trabajo/vw-trae-tu-trabajo.vue"),
    meta: { titulo: "Trae tu trabajo", seccion: SeccionNavEnum.GUIA },
  },
  {
    path: "/revision",
    name: RutaEnum.REVISION,
    component: () => import("@/views/vw-revision/vw-revision.vue"),
    meta: { titulo: "Revisión de afirmaciones", seccion: SeccionNavEnum.GUIA },
  },
  {
    path: "/herramientas",
    name: RutaEnum.HERRAMIENTAS,
    component: () => import("@/views/vw-herramientas/vw-herramientas.vue"),
    meta: { titulo: "Herramientas recomendadas", seccion: SeccionNavEnum.GUIA },
  },
  {
    path: "/cierre",
    name: RutaEnum.CIERRE,
    component: () => import("@/views/vw-cierre/vw-cierre.vue"),
    meta: { titulo: "Cierre del recorrido", seccion: SeccionNavEnum.GUIA },
  },
  {
    path: "/ajustes",
    name: RutaEnum.AJUSTES,
    component: () => import("@/views/vw-ajustes/vw-ajustes.vue"),
    meta: { titulo: "Ajustes" },
  },
  {
    path: "/rol",
    name: RutaEnum.ROL,
    component: () => import("@/views/vw-rol/vw-rol.vue"),
    meta: { titulo: "Elige cómo usar FROBI", seccion: SeccionNavEnum.INICIO },
  },
  {
    path: "/intro",
    name: RutaEnum.INTRO,
    component: () => import("@/views/vw-intro/vw-intro.vue"),
    meta: { titulo: "Introducción a la IA", seccion: SeccionNavEnum.INICIO },
  },
  {
    path: "/perfil-accesibilidad",
    name: RutaEnum.PERFIL_ACCESIBILIDAD,
    component: () => import("@/views/vw-perfil-accesibilidad/vw-perfil-accesibilidad.vue"),
    meta: { titulo: "Cómo aprendes mejor", seccion: SeccionNavEnum.INICIO },
  },
  {
    path: "/asistente/:paso",
    name: RutaEnum.ASISTENTE,
    component: () => import("@/views/vw-asistente/vw-asistente.vue"),
    meta: { titulo: "Primera configuración" },
  },
  { path: "/asistente", redirect: { name: RutaEnum.ASISTENTE, params: { paso: 1 } } },
  {
    path: "/guia/:tarea/ayuda",
    name: RutaEnum.AYUDA,
    component: () => import("@/views/vw-ayuda/vw-ayuda.vue"),
    meta: { titulo: "Escalera de ayuda", seccion: SeccionNavEnum.GUIA },
  },
  {
    path: "/guia/:tarea/sin-ia",
    name: RutaEnum.SIN_IA,
    component: () => import("@/views/vw-sin-ia/vw-sin-ia.vue"),
    meta: { titulo: "Inténtalo sin IA", seccion: SeccionNavEnum.GUIA },
  },
  {
    path: "/docente/clase/nueva",
    name: RutaEnum.CLASE_NUEVA,
    component: () => import("@/views/vw-clase-nueva/vw-clase-nueva.vue"),
    meta: { titulo: "Crear clase", seccion: SeccionNavEnum.DOCENTE },
  },
  {
    path: "/docente/clase/invitar",
    name: RutaEnum.CLASE_INVITAR,
    component: () => import("@/views/vw-clase-invitar/vw-clase-invitar.vue"),
    meta: { titulo: "Invitar alumnos", seccion: SeccionNavEnum.DOCENTE },
  },
  {
    path: "/docente/alumno/:alias",
    name: RutaEnum.ALUMNO,
    component: () => import("@/views/vw-alumno/vw-alumno.vue"),
    meta: { titulo: "Detalle del alumno", seccion: SeccionNavEnum.DOCENTE },
  },
  {
    path: "/como-se-usa",
    name: RutaEnum.COMO_SE_USA,
    component: () => import("@/views/vw-como-se-usa/vw-como-se-usa.vue"),
    meta: { titulo: "Cómo se usa" },
  },
  {
    path: "/demo/personas",
    name: RutaEnum.PERSONAS,
    component: () => import("@/views/vw-personas/vw-personas.vue"),
    meta: { titulo: "Distintas personas" },
  },
  { path: "/:pathMatch(.*)*", redirect: { name: RutaEnum.INICIO } },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior: (_to, _from, guardada) => guardada ?? { top: 0 },
});

// Pantallas que se ven sin entrar: el login y las de presentación (Figma · 21 y 23).
const RUTAS_PUBLICAS: string[] = [RutaEnum.LOGIN, RutaEnum.COMO_SE_USA, RutaEnum.PERSONAS];

router.beforeEach((to) => {
  const sesion = useCmpSesionStore();
  if (!RUTAS_PUBLICAS.includes(to.name as string) && !sesion.haIniciado) {
    return { name: RutaEnum.LOGIN, query: { volver: to.fullPath } };
  }
  if (to.name === RutaEnum.LOGIN && sesion.haIniciado) {
    return { name: RutaEnum.INICIO };
  }
});

// Si la API responde 401 (token vencido o cerrado), se vuelve a "Entrar".
registrarAlPerderSesion(() => {
  useCmpSesionStore().olvidarSesion();
  const actual = router.currentRoute.value;
  if (!RUTAS_PUBLICAS.includes(actual.name as string)) {
    router.push({ name: RutaEnum.LOGIN, query: { volver: actual.fullPath } });
  }
});

router.afterEach((to) => {
  document.title = `${to.meta.titulo} · FROBI`;
});

export default router;
