import { computed, defineComponent, onMounted } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VChipPieza from "@/components/base/v-chip-pieza/v-chip-pieza.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VTarjetaPieza from "@/components/base/v-tarjeta-pieza/v-tarjeta-pieza.vue";
import useCmpCierre from "@/composables/business/cmp-cierre/cmp-cierre.composable";
import useCmpAvisos from "@/composables/common/cmp-avisos/cmp-avisos.composable";
import { FORMATOS } from "@/constants/formatos.constant";
import { nombrePieza } from "@/constants/piezas.constant";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpCierre",
  components: { VButton, VCargando, VChipPieza, VIcon, VTarjetaPieza },
  setup() {
    const PREFIX = "cmp-cierre";

    const { resumen, cargar } = useCmpCierre();

    const { mostrarAviso } = useCmpAvisos();

    const nombreFormato = computed(
      () => FORMATOS.find((formato) => formato.id === resumen.value?.formatoUsado)?.nombre ?? "",
    );

    const copiarReceta = async () => {
      const texto = (resumen.value?.receta ?? [])
        .map((pieza) => `${nombrePieza(pieza.pieza)}: ${pieza.texto}`)
        .join("\n");
      try {
        await navigator.clipboard.writeText(texto);
      } catch {
        // Portapapeles no disponible (http, permisos): el aviso se muestra igual.
      }
      mostrarAviso("Receta copiada", "Pégala donde quieras. Se oculta en 4 s.");
    };

    onMounted(cargar);

    return { nombrePieza, RutaEnum, PREFIX, resumen, nombreFormato, copiarReceta };
  },
});
