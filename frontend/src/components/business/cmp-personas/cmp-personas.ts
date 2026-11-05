import { defineComponent } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import { PERSONAS_MOCK } from "@/mocks/presentacion.mock";

export default defineComponent({
  name: "CmpPersonas",
  components: { VIcon },
  setup() {
    const PREFIX = "cmp-personas";

    // En escritorio la segunda fila tiene 2 tarjetas anchas (Figma · 23).
    const ANCHAS = ["marco", "pedro"];

    return { PERSONAS_MOCK, PREFIX, ANCHAS };
  },
});
