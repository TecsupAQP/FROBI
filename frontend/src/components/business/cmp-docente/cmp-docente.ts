import { defineComponent, onMounted } from "vue";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VBarraDato from "@/components/base/v-barra-dato/v-barra-dato.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VSelect from "@/components/base/v-select/v-select.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VEstadoVacio from "@/components/base/v-estado-vacio/v-estado-vacio.vue";
import CmpMiClase from "@/components/business/cmp-docente/content/cmp-mi-clase/cmp-mi-clase.vue";
import CmpContenidoClase from "@/components/business/cmp-docente/content/cmp-contenido-clase/cmp-contenido-clase.vue";
import useCmpClase from "@/composables/common/cmp-clase/cmp-clase.composable";
import useCmpDocente from "@/composables/business/cmp-docente/cmp-docente.composable";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpDocente",
  components: {
    VAviso,
    VBarraDato,
    VButton,
    VCargando,
    VEstadoVacio,
    VIcon,
    VSelect,
    CmpEncabezadoPagina,
    VChip,
    CmpMiClase,
    CmpContenidoClase,
  },
  setup() {
    const PREFIX = "cmp-docente";

    const { cargado, grupoId, panel, cambiarGrupo, cargar } = useCmpDocente();

    const {
      clase,
      contenido,
      errorContenido,
      subiendo,
      cargar: cargarClase,
      cargarContenido,
      subirContenido,
    } = useCmpClase();

    onMounted(async () => {
      // Se recarga siempre: el docente pudo crear otra clase o cambiar de clase.
      await Promise.all([cargar(), cargarClase(true)]);
      await cargarContenido();
    });

    return {
      RutaEnum,
      PREFIX,
      cargado,
      grupoId,
      panel,
      cambiarGrupo,
      clase,
      contenido,
      errorContenido,
      subiendo,
      subirContenido,
    };
  },
});
