import { defineComponent, type PropType } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { Sugerencia } from "@/core/shared/domain/view/prompt-score.view";

export default defineComponent({
  name: "CmpSugerencia",
  components: { VButton, VCargando, VIcon },
  props: {
    sugerencia: { type: Object as PropType<Sugerencia>, required: true },
    ocupado: { type: Boolean, default: false },
  },
  emits: {
    mejorar: () => true,
    anadir: () => true,
  },
  setup() {
    const PREFIX = "cmp-sugerencia";

    return { PREFIX };
  },
});
