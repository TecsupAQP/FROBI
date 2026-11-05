import { defineComponent } from "vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import { RECORRIDO_MOCK } from "@/mocks/presentacion.mock";

export default defineComponent({
  name: "CmpComoSeUsa",
  components: { VChip, VIcon },
  setup() {
    const PREFIX = "cmp-como-se-usa";

    return { RECORRIDO_MOCK, PREFIX };
  },
});
