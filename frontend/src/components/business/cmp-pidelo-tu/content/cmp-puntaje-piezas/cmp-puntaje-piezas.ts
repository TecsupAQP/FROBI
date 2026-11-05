import { defineComponent, type PropType } from "vue";
import VChipPieza from "@/components/base/v-chip-pieza/v-chip-pieza.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { PromptScore } from "@/core/shared/domain/view/prompt-score.view";

export default defineComponent({
  name: "CmpPuntajePiezas",
  components: { VChipPieza, VIcon },
  props: {
    evaluacion: { type: Object as PropType<PromptScore>, required: true },
  },
  setup() {
    const PREFIX = "cmp-puntaje-piezas";

    return { PREFIX };
  },
});
