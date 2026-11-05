import { computed, defineComponent, nextTick, onBeforeUnmount, onMounted, ref, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import VButton from "@/components/base/v-button/v-button.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VPasos from "@/components/base/v-pasos/v-pasos.vue";
import useCmpRecorrido from "@/composables/common/cmp-recorrido/cmp-recorrido.composable";
import { RutaEnum } from "@/enums/ruta.enum";

// Pantallas donde el recorrido se ofrece solo la primera vez.
const INICIOS: string[] = [RutaEnum.INICIO, RutaEnum.CLASE_NUEVA, RutaEnum.DOCENTE];
const ESPERA_MAXIMA_MS = 1500;
const MARGEN_SUPERIOR = 96;
const HOLGURA = 8;

interface Marco {
  top: number;
  left: number;
  width: number;
  height: number;
}

// Recorrido guiado: lleva a cada pantalla y resalta la parte de la que habla. No bloquea la app:
// la persona puede tocar lo resaltado mientras lee.
export default defineComponent({
  name: "CmpRecorrido",
  components: { VButton, VIcon, VPasos },
  setup() {
    const PREFIX = "cmp-recorrido";

    const route = useRoute();

    const router = useRouter();

    const {
      activo,
      esPrimero,
      esUltimo,
      indice,
      paso,
      pasos,
      anterior,
      debeMostrarse,
      iniciar,
      siguiente,
      terminar,
    } = useCmpRecorrido();

    const titulo = ref<HTMLElement | null>(null);

    const objetivo = ref<HTMLElement | null>(null);

    const marco = ref<Marco | null>(null);

    const buscando = ref(false);

    // El paso no encontró su parte en pantalla (por ejemplo, todavía no hay guía).
    const falta = computed(() => !buscando.value && !!paso.value?.objetivo && !objetivo.value);

    const estiloMarco = computed(() =>
      marco.value
        ? {
            top: `${marco.value.top}px`,
            left: `${marco.value.left}px`,
            width: `${marco.value.width}px`,
            height: `${marco.value.height}px`,
          }
        : undefined,
    );

    const medir = () => {
      const rect = objetivo.value?.getBoundingClientRect();
      marco.value = rect
        ? {
            top: rect.top - HOLGURA,
            left: rect.left - HOLGURA,
            width: rect.width + HOLGURA * 2,
            height: rect.height + HOLGURA * 2,
          }
        : null;
    };

    let cuadro = 0;
    const alMover = () => {
      cancelAnimationFrame(cuadro);
      cuadro = requestAnimationFrame(medir);
    };

    const esperarObjetivo = async (nombre: string): Promise<HTMLElement | null> => {
      const limite = Date.now() + ESPERA_MAXIMA_MS;
      while (Date.now() < limite) {
        const encontrado = document.querySelector<HTMLElement>(`[data-recorrido="${nombre}"]`);
        if (encontrado) return encontrado;
        await new Promise((resolver) => setTimeout(resolver, 100));
      }
      return null;
    };

    let pedido = 0;
    const mostrarPaso = async () => {
      const actual = paso.value;
      const numero = ++pedido;
      objetivo.value = null;
      marco.value = null;
      if (!actual) return;
      buscando.value = true;
      if (actual.destino && route.name !== actual.ruta) await router.push(actual.destino);
      // Si la app redirigió (por ejemplo, sin guía), no se busca la parte en otra pantalla.
      const enSuPantalla = !actual.ruta || route.name === actual.ruta;
      const encontrado = actual.objetivo && enSuPantalla ? await esperarObjetivo(actual.objetivo) : null;
      if (numero !== pedido) return;
      buscando.value = false;
      objetivo.value = encontrado;
      if (encontrado) {
        const arriba = encontrado.getBoundingClientRect().top + window.scrollY - MARGEN_SUPERIOR;
        const suave = !window.matchMedia("(prefers-reduced-motion: reduce)").matches;
        window.scrollTo({ top: Math.max(0, arriba), behavior: suave ? "smooth" : "auto" });
        medir();
      }
      await nextTick();
      titulo.value?.focus();
    };

    const salir = () => terminar();

    const alPresionar = (evento: KeyboardEvent) => {
      if (activo.value && evento.key === "Escape") salir();
    };

    watch([activo, indice], mostrarPaso);

    onMounted(() => {
      window.addEventListener("scroll", alMover, { passive: true });
      window.addEventListener("resize", alMover);
      window.addEventListener("keydown", alPresionar);
      if (activo.value) {
        mostrarPaso();
      } else if (debeMostrarse() && INICIOS.includes(route.name as string)) {
        window.setTimeout(() => {
          if (!activo.value && debeMostrarse()) iniciar();
        }, 700);
      }
    });

    onBeforeUnmount(() => {
      window.removeEventListener("scroll", alMover);
      window.removeEventListener("resize", alMover);
      window.removeEventListener("keydown", alPresionar);
      cancelAnimationFrame(cuadro);
    });

    return {
      PREFIX,
      activo,
      paso,
      pasos,
      indice,
      esPrimero,
      esUltimo,
      buscando,
      falta,
      marco,
      estiloMarco,
      titulo,
      anterior,
      siguiente,
      salir,
    };
  },
});
