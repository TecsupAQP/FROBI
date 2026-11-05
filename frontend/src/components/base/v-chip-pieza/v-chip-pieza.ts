import { defineComponent, type PropType } from "vue";
import { nombrePieza } from "@/constants/piezas.constant";
import type { PiezaId } from "@/core/shared/domain/view/pieza.view";

export default defineComponent({
  name: "VChipPieza",
  props: {
    pieza: { type: String as PropType<PiezaId>, required: true },
    compacto: { type: Boolean, default: false },
  },
  setup() {
    const PREFIX = "v-chip-pieza";

    return { nombrePieza, PREFIX };
  },
});
