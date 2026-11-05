import { defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import { SEMAFORO } from "@/constants/semaforo.constant";
import type { EstadoAfirmacion } from "@/core/shared/domain/view/claim-review.view";

export default defineComponent({
  name: "VSemaforo",
  components: { VIcon },
  props: {
    estado: { type: String as PropType<EstadoAfirmacion>, required: true },
  },
  setup() {
    const PREFIX = "v-semaforo";

    return { SEMAFORO, PREFIX };
  },
});
