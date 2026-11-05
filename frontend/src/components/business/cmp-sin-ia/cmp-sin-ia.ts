import { defineComponent, onMounted, ref } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VCasilla from "@/components/base/v-casilla/v-casilla.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VField from "@/components/base/v-field/v-field.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import useCmpAvisos from "@/composables/common/cmp-avisos/cmp-avisos.composable";
import useCmpEscalera from "@/composables/business/cmp-escalera/cmp-escalera.composable";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpSinIa",
  components: { VButton, VCargando, VCasilla, VChip, VField, CmpEncabezadoPagina },
  props: {
    tareaId: { type: String, required: true },
  },
  setup(props) {
    const PREFIX = "cmp-sin-ia";

    const {
      criterios,
      error,
      probando,
      progreso,
      tarea,
      alternarCriterio,
      cargar,
      escribirRespuestaSinIa,
      marcarResueltoSinIa,
    } = useCmpEscalera();

    const { mostrarAviso } = useCmpAvisos();

    const comparado = ref(false);

    const comparar = async () => {
      const logro = await marcarResueltoSinIa();
      if (error.value) return;
      comparado.value = true;
      if (logro) mostrarAviso("Resuelto sin IA", "Cuenta como logro en tu progreso.");
      else mostrarAviso("Comparado con tu guía", "Revisa tu respuesta con lo que dice tu guía.");
    };

    onMounted(() => cargar(props.tareaId));

    return {
      RutaEnum,
      PREFIX,
      criterios,
      error,
      probando,
      progreso,
      tarea,
      comparado,
      alternarCriterio,
      escribirRespuestaSinIa,
      comparar,
    };
  },
});
