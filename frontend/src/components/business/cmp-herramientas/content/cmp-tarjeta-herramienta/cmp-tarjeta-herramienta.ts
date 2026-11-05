import { defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { Tool } from "@/core/shared/domain/view/tool.view";

export default defineComponent({
  name: "CmpTarjetaHerramienta",
  components: { VIcon },
  props: {
    herramienta: { type: Object as PropType<Tool>, required: true },
  },
  setup() {
    const PREFIX = "cmp-tarjeta-herramienta";

    return { PREFIX };
  },
});
