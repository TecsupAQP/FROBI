import { defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { NombreIcono } from "@/constants/iconos.constant";

export default defineComponent({
  name: "VChip",
  components: { VIcon },
  props: {
    tono: {
      type: String as PropType<"marca" | "marino" | "suave" | "exito" | "aviso" | "error" | "neutro">,
      default: "suave",
    },
    icono: { type: String as PropType<NombreIcono>, default: undefined },
  },
  setup() {
    const PREFIX = "v-chip";

    return { PREFIX };
  },
});
