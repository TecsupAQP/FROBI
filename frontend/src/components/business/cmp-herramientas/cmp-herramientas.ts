import { defineComponent, onMounted } from "vue";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import CmpEncabezadoPagina from "@/components/common/cmp-encabezado-pagina/cmp-encabezado-pagina.vue";
import CmpTarjetaHerramienta from "@/components/business/cmp-herramientas/content/cmp-tarjeta-herramienta/cmp-tarjeta-herramienta.vue";
import useCmpHerramientas from "@/composables/business/cmp-herramientas/cmp-herramientas.composable";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpHerramientas",
  components: { VAviso, VButton, VCargando, VIcon, CmpEncabezadoPagina, CmpTarjetaHerramienta },
  setup() {
    const PREFIX = "cmp-herramientas";

    const { necesidad, nombreNecesidad, otras, recomendacion, recomendada, cargar, elegirNecesidad } =
      useCmpHerramientas();

    onMounted(cargar);

    return {
      RutaEnum,
      PREFIX,
      necesidad,
      nombreNecesidad,
      otras,
      recomendacion,
      recomendada,
      elegirNecesidad,
    };
  },
});
