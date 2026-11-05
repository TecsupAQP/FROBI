import { defineComponent, type PropType } from "vue";
import VSemaforo from "@/components/base/v-semaforo/v-semaforo.vue";
import type { ClaimReview } from "@/core/shared/domain/view/claim-review.view";

export default defineComponent({
  name: "CmpAfirmacion",
  components: { VSemaforo },
  props: {
    afirmacion: { type: Object as PropType<ClaimReview>, required: true },
  },
  setup() {
    const PREFIX = "cmp-afirmacion";

    return { PREFIX };
  },
});
