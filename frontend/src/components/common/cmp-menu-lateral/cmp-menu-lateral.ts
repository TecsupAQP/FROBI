import { computed, defineComponent, nextTick, onBeforeUnmount, ref, useModel, watch } from "vue";
import { useRoute, useRouter, type RouteLocationRaw } from "vue-router";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import useCmpRecorrido from "@/composables/common/cmp-recorrido/cmp-recorrido.composable";
import useCmpSesion from "@/composables/common/cmp-sesion/cmp-sesion.composable";
import type { NombreIcono } from "@/constants/iconos.constant";
import { RutaEnum, TAREA_EJEMPLO } from "@/enums/ruta.enum";

interface EnlaceMenu {
  nombre: string;
  icono: NombreIcono;
  destino: RouteLocationRaw;
  // Ruta que lo marca como página actual.
  ruta: RutaEnum;
}

interface GrupoMenu {
  titulo: string;
  enlaces: EnlaceMenu[];
}

const ENFOCABLES = 'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])';

// Menú con todas las pantallas: la barra superior solo muestra 3 pestañas (Figma).
export default defineComponent({
  name: "CmpMenuLateral",
  components: { VIcon },
  props: {
    modelValue: { type: Boolean, default: false },
  },
  emits: {
    "update:modelValue": (_valor: boolean) => true,
  },
  setup(props) {
    const PREFIX = "cmp-menu-lateral";

    const abierto = useModel(props, "modelValue");

    const route = useRoute();

    const router = useRouter();

    const { estudiante, esDocente, cerrarSesion } = useCmpSesion();

    const panel = ref<HTMLElement | null>(null);

    const enlace = (nombre: string, icono: NombreIcono, ruta: RutaEnum, destino?: RouteLocationRaw) => ({
      nombre,
      icono,
      ruta,
      destino: destino ?? { name: ruta },
    });

    const grupos = computed<GrupoMenu[]>(() => {
      const docente: GrupoMenu = {
        titulo: "Mi clase",
        enlaces: [
          enlace("Panel docente", "chart", RutaEnum.DOCENTE),
          enlace("Crear clase", "pencil", RutaEnum.CLASE_NUEVA),
          enlace("Invitar alumnos", "users", RutaEnum.CLASE_INVITAR),
        ],
      };
      const estudiar: GrupoMenu = {
        titulo: "Estudiar",
        enlaces: [
          enlace("Inicio y mis guías", "book", RutaEnum.INICIO),
          enlace("Guía y formatos", "map", RutaEnum.GUIA),
          enlace("Escalera de ayuda", "help", RutaEnum.AYUDA, {
            name: RutaEnum.AYUDA,
            params: { tarea: TAREA_EJEMPLO },
          }),
          enlace("Inténtalo sin IA", "star", RutaEnum.SIN_IA, {
            name: RutaEnum.SIN_IA,
            params: { tarea: TAREA_EJEMPLO },
          }),
          enlace("Verifica lo que aprendiste", "check-circle", RutaEnum.VERIFICACION),
          enlace("Pídelo tú", "spark", RutaEnum.PIDELO_TU),
        ],
      };
      const trabajo: GrupoMenu = {
        titulo: "Mi trabajo",
        enlaces: [
          enlace("Trae tu trabajo", "upload", RutaEnum.TRAE_TU_TRABAJO),
          enlace("Revisión de afirmaciones", "search", RutaEnum.REVISION),
          enlace("Herramientas recomendadas", "org", RutaEnum.HERRAMIENTAS),
        ],
      };
      const avance: GrupoMenu = {
        titulo: "Mi avance",
        enlaces: [
          enlace("Mi progreso", "gauge", RutaEnum.PROGRESO),
          enlace("Cierre del recorrido", "check", RutaEnum.CIERRE),
        ],
      };
      const cuenta: GrupoMenu = {
        titulo: "Cuenta y ayuda",
        enlaces: [
          enlace("Pregúntale a FROBI", "spark", RutaEnum.CHAT),
          enlace("Ajustes", "user", RutaEnum.AJUSTES),
          enlace("Cómo aprendes mejor", "eye", RutaEnum.PERFIL_ACCESIBILIDAD),
          enlace("Cómo se usa FROBI", "info", RutaEnum.COMO_SE_USA),
        ],
      };
      return esDocente.value ? [docente, estudiar, cuenta] : [estudiar, trabajo, avance, cuenta];
    });

    const cerrar = () => {
      abierto.value = false;
    };

    const { iniciar: iniciarRecorrido } = useCmpRecorrido();

    // Repite el recorrido guiado de su rol.
    const verRecorrido = () => {
      cerrar();
      iniciarRecorrido();
    };

    const salir = async () => {
      cerrar();
      try {
        await cerrarSesion();
      } finally {
        router.push({ name: RutaEnum.LOGIN });
      }
    };

    // Mantiene el foco dentro del panel y cierra con Escape.
    const alPresionar = (evento: KeyboardEvent) => {
      if (evento.key === "Escape") {
        evento.stopPropagation();
        cerrar();
        return;
      }
      if (evento.key !== "Tab" || !panel.value) return;
      const enfocables = [...panel.value.querySelectorAll<HTMLElement>(ENFOCABLES)];
      const primero = enfocables[0];
      const ultimo = enfocables[enfocables.length - 1];
      if (!primero || !ultimo) return;
      if (evento.shiftKey && document.activeElement === primero) {
        evento.preventDefault();
        ultimo.focus();
      } else if (!evento.shiftKey && document.activeElement === ultimo) {
        evento.preventDefault();
        primero.focus();
      }
    };

    let focoPrevio: HTMLElement | null = null;

    watch(abierto, async (valor) => {
      document.body.style.overflow = valor ? "hidden" : "";
      if (valor) {
        focoPrevio = document.activeElement as HTMLElement | null;
        await nextTick();
        // El foco va a la página actual (o al primer enlace) para seguir con el teclado.
        const actual =
          panel.value?.querySelector<HTMLElement>('[aria-current="page"]') ??
          panel.value?.querySelector<HTMLElement>("a[href]");
        (actual ?? panel.value)?.focus();
      } else {
        focoPrevio?.focus();
      }
    });

    // Al navegar desde el menú, se cierra.
    watch(
      () => route.fullPath,
      () => cerrar(),
    );

    onBeforeUnmount(() => {
      document.body.style.overflow = "";
    });

    return {
      RutaEnum,
      PREFIX,
      abierto,
      panel,
      estudiante,
      grupos,
      route,
      cerrar,
      salir,
      verRecorrido,
      alPresionar,
    };
  },
});
