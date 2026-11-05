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

    const BLOQUEOS: Record<EscalonId, string> = {
      "pista-1": "",
      "pista-2": "",
      "paso-a-paso": "Se abre si lo necesitas.",
      respuesta: "Se desbloquea después de tu intento.",
    };

    const {
      error,
      nivelAyuda,
      probando,
      progreso,
      respuestaDesbloqueada,
      tarea,
      abrirPasoAPaso,
      abrirPistas,
      cargar,
      escribirIntento,
      probarIntento,
    } = useCmpEscalera();

    const { ajustes } = useCmpAjustes();

    const { vozActiva, leer } = useVoz();

    const estadoDe = (id: EscalonId): EstadoEscalon => {
      switch (id) {
        case "pista-1":
          return "hecho";
        case "pista-2":
          return progreso.value.resultado ? "hecho" : "activo";
        case "paso-a-paso":
          return progreso.value.pasoAPasoAbierto ? "abierto" : "bloqueado";
        case "respuesta":
          // La respuesta final llega al último y solo después de un intento propio.
          return respuestaDesbloqueada.value ? "abierto" : "bloqueado";
      }
    };

    // "Textos cortos, un paso a la vez": se ocultan los escalones bloqueados.
    const escalonesVisibles = computed(() => {
      const todos = tarea.value?.escalones ?? [];
      return ajustes.value.activos["textos-cortos"]
        ? todos.filter((escalon) => estadoDe(escalon.id) !== "bloqueado")
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

    onMounted(async () => {
      await cargar(props.tareaId);
      await abrirPistas();
    });

    return {
      RutaEnum,
      PREFIX,
      BLOQUEOS,
      error,
      nivelAyuda,
      probando,
      progreso,
      tarea,
      abrirPasoAPaso,
      escribirIntento,
      probarIntento,
      estadoDe,
      escalonesVisibles,
      escalonesOcultos,
    };
  },
});
