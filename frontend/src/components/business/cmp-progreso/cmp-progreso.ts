import { defineComponent, onMounted } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VEstadoVacio from "@/components/base/v-estado-vacio/v-estado-vacio.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import CmpEvolucion from "@/components/business/cmp-progreso/content/cmp-evolucion/cmp-evolucion.vue";
import useCmpProgreso from "@/composables/business/cmp-progreso/cmp-progreso.composable";
import { FORMATOS } from "@/constants/formatos.constant";
import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";
import { EstadoCargaEnum } from "@/core/shared/application/enum/estado-carga.enum";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpProgreso",
  components: { VButton, VCargando, VEstadoVacio, VIcon, CmpEncabezadoPagina, CmpEvolucion },
  props: {
    alias: { type: String, required: true },
  },
  setup(props) {
    const PREFIX = "cmp-progreso";

    const { estado, progreso, cargar } = useCmpProgreso();

    const nombreFormato = (id: FormatoId) => FORMATOS.find((formato) => formato.id === id)?.nombreCorto ?? id;

    onMounted(() => cargar(props.alias));

    return { EstadoCargaEnum, RutaEnum, PREFIX, estado, progreso, nombreFormato };
  },
});
