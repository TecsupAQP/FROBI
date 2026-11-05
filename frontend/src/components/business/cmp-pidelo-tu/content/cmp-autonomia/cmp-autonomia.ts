import { defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { Autonomia, EstadoNivel } from "@/core/shared/domain/view/prompt-score.view";

export default defineComponent({
  name: "CmpAutonomia",
  components: { VIcon },
  props: {
    autonomia: { type: Object as PropType<Autonomia>, required: true },
  },
  setup() {
    const PREFIX = "cmp-autonomia";

    // El estado se dice con texto además del color y el icono.
    const SUFIJOS: Record<EstadoNivel, string> = {
      superado: " · superado",
      actual: " · estás aquí",
      bloqueado: "",
    };

    return { PREFIX, SUFIJOS };
  },
});
