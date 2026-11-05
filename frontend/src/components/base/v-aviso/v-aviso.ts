import { defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { NombreIcono } from "@/constants/iconos.constant";

type TipoAviso = "info" | "nota" | "aviso" | "exito" | "error";

export default defineComponent({
  name: "VAviso",
  components: { VIcon },
  props: {
    tipo: { type: String as PropType<TipoAviso>, default: "info" },
    icono: { type: String as PropType<NombreIcono>, default: undefined },
  },
  setup() {
    const PREFIX = "v-aviso";

    const ICONO_POR_TIPO: Record<TipoAviso, NombreIcono> = {
      info: "info",
      nota: "info",
      aviso: "warn",
      exito: "info",
      error: "warn",
    };

    return { PREFIX, ICONO_POR_TIPO };
  },
});
