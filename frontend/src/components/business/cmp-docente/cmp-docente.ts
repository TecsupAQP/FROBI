import { defineComponent, onMounted } from "vue";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VBarraDato from "@/components/base/v-barra-dato/v-barra-dato.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VSelect from "@/components/base/v-select/v-select.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import CmpMiClase from "@/components/business/cmp-docente/content/cmp-mi-clase/cmp-mi-clase.vue";
import useCmpClase from "@/composables/common/cmp-clase/cmp-clase.composable";
import useCmpDocente from "@/composables/business/cmp-docente/cmp-docente.composable";

export default defineComponent({
  name: "CmpDocente",
  components: { VAviso, VBarraDato, VCargando, VIcon, VSelect, CmpEncabezadoPagina, VChip, CmpMiClase },
  setup() {
    const PREFIX = "cmp-docente";

    const { grupoId, panel, cambiarGrupo, cargar } = useCmpDocente();

    const { clase, cargar: cargarClase } = useCmpClase();

    onMounted(() => {
      cargar();
      cargarClase();
    });

    return { PREFIX, grupoId, panel, cambiarGrupo, clase };
  },
});
