import { defineComponent, type PropType } from "vue";
import VSemaforo from "@/components/base/v-semaforo/v-semaforo.vue";
import CmpAfirmacion from "@/components/business/cmp-revision/content/cmp-afirmacion/cmp-afirmacion.vue";
import type { SeccionRevisada } from "@/core/shared/domain/view/claim-review.view";

export default defineComponent({
  name: "CmpSeccionRevisada",
  components: { VSemaforo, CmpAfirmacion },
  props: {
    seccion: { type: Object as PropType<SeccionRevisada>, required: true },
  },
  setup() {
    const PREFIX = "cmp-seccion-revisada";

    return { PREFIX };
  },
});
