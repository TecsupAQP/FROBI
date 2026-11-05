import { defineComponent, type PropType } from "vue";
import { nombrePieza } from "@/constants/piezas.constant";
import type { PiezaId } from "@/core/shared/domain/view/pieza.view";

export default defineComponent({
  name: "VTarjetaPieza",
  props: {
    pieza: { type: String as PropType<PiezaId>, required: true },
  },
  setup() {
    const PREFIX = "v-tarjeta-pieza";

    return { nombrePieza, PREFIX };
  },
});
