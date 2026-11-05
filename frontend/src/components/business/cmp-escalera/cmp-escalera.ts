import { computed, defineComponent, onMounted, watch } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VEstadoVacio from "@/components/base/v-estado-vacio/v-estado-vacio.vue";
import VField from "@/components/base/v-field/v-field.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import CmpEscalon from "@/components/business/cmp-escalera/content/cmp-escalon/cmp-escalon.vue";
import useCmpAjustes from "@/composables/common/cmp-ajustes/cmp-ajustes.composable";
import useCmpEscalera from "@/composables/business/cmp-escalera/cmp-escalera.composable";
import useVoz from "@/composables/common/voz/voz.composable";
import type { EscalonId, EstadoEscalon } from "@/core/shared/domain/view/ayuda.view";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpEscalera",
  components: { VButton, VCargando, VChip, VEstadoVacio, VField, VIcon, CmpEncabezadoPagina, CmpEscalon },
  props: {
    tareaId: { type: String, required: true },
  },
  setup(props) {
    const PREFIX = "cmp-escalera";

    const ORDEN: EscalonId[] = ["pista-1", "pista-2", "paso-a-paso", "respuesta"];

    const {
      abriendo,
      error,
      nivelAyuda,
      probando,
      progreso,
      respuestaDesbloqueada,
      siguiente,
      tarea,
      abrirSiguiente,
      cargar,
      escribirIntento,
      probarIntento,
    } = useCmpEscalera();

    const { ajustes } = useCmpAjustes();

    const { vozActiva, leer } = useVoz();

    const indiceAlcanzado = computed(() =>
      progreso.value.alcanzado ? ORDEN.indexOf(progreso.value.alcanzado) : -1,
    );

    // Los escalones abiertos quedan "hechos"; el último abierto es el actual. Nada se abre solo (RF39).
    const estadoDe = (id: EscalonId): EstadoEscalon => {
      const indice = ORDEN.indexOf(id);
      if (indice < indiceAlcanzado.value) return "hecho";
      if (indice === indiceAlcanzado.value) return id === "respuesta" ? "abierto" : "activo";
      return "bloqueado";
    };

    const tituloDe = (id: EscalonId) =>
      tarea.value?.escalones.find((escalon) => escalon.id === id)?.titulo ?? "";

    // Qué dice un escalón cerrado: si se puede pedir ya, o qué falta para pedirlo.
    const textoBloqueo = (id: EscalonId): string => {
      if (id === siguiente.value) return id === "paso-a-paso" ? "Se abre si lo necesitas." : "";
      if (id === "respuesta" && !respuestaDesbloqueada.value) return "Se desbloquea después de tu intento.";
      const anterior = ORDEN[ORDEN.indexOf(id) - 1];
      return anterior ? `Se abre después de ${tituloDe(anterior).toLowerCase()}.` : "";
    };

    // "Textos cortos, un paso a la vez": se ocultan los escalones bloqueados.
    const escalonesVisibles = computed(() => {
      const todos = tarea.value?.escalones ?? [];
      return ajustes.value.activos["textos-cortos"]
        ? todos.filter((escalon) => estadoDe(escalon.id) !== "bloqueado" || escalon.id === siguiente.value)
        : todos;
    });

    const escalonesOcultos = computed(
      () => (tarea.value?.escalones.length ?? 0) > escalonesVisibles.value.length,
    );

    // "La voz lee cada paso": se lee la pista activa cuando cambia.
    const textoActivo = computed(() => {
      const activo = tarea.value?.escalones.find((escalon) =>
        ["activo", "abierto"].includes(estadoDe(escalon.id)),
      );
      return activo ? `${activo.titulo}. ${activo.contenido.join(" ")}` : "";
    });

    watch(textoActivo, (texto) => {
      if (vozActiva.value && texto) leer(texto);
    });

    onMounted(() => cargar(props.tareaId));

    return {
      RutaEnum,
      PREFIX,
      abriendo,
      error,
      nivelAyuda,
      probando,
      progreso,
      siguiente,
      tarea,
      abrirSiguiente,
      escribirIntento,
      probarIntento,
      estadoDe,
      textoBloqueo,
      tituloDe,
      escalonesVisibles,
      escalonesOcultos,
    };
  },
});
