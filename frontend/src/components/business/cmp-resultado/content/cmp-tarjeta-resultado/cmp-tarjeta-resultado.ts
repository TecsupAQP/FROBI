import { defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { DefinicionFormato } from "@/constants/formatos.constant";

export default defineComponent({
  name: "CmpTarjetaResultado",
  components: { VIcon },
  props: {
    formato: { type: Object as PropType<DefinicionFormato>, required: true },
    tema: { type: String, required: true },
  },
  setup() {
    const PREFIX = "cmp-tarjeta-resultado";

    return { PREFIX };
  },
});
