import { defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { Tema } from "@/core/shared/domain/view/material.view";

export default defineComponent({
  name: "CmpTema",
  components: { VIcon },
  props: {
    tema: { type: Object as PropType<Tema>, required: true },
    abierto: { type: Boolean, required: true },
  },
  emits: {
    alternar: (_temaId: string) => true,
  },
  setup() {
    const PREFIX = "cmp-tema";

    return { PREFIX };
  },
});
