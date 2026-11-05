import { defineComponent, type PropType } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VTarjetaPieza from "@/components/base/v-tarjeta-pieza/v-tarjeta-pieza.vue";
import type { PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";

export default defineComponent({
  name: "CmpRecetaIa",
  components: { VButton, VIcon, VTarjetaPieza },
  props: {
    receta: { type: Array as PropType<PiezaInstruccion[]>, required: true },
    desplegada: { type: Boolean, required: true },
  },
  emits: {
    alternar: () => true,
    copiar: () => true,
  },
  setup() {
    const PREFIX = "cmp-receta-ia";

    return { PREFIX };
  },
});
