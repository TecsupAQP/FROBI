import { defineComponent, type PropType } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VTarjetaPieza from "@/components/base/v-tarjeta-pieza/v-tarjeta-pieza.vue";
import type { PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";

export default defineComponent({
  name: "CmpPlantilla",
  components: { VButton, VIcon, VTarjetaPieza },
  props: {
    plantilla: { type: Array as PropType<PiezaInstruccion[]>, required: true },
  },
  emits: {
    usar: () => true,
  },
  setup() {
    const PREFIX = "cmp-plantilla";

    return { PREFIX };
  },
});
