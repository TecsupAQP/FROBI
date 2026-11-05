import { defineComponent, type PropType } from "vue";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";

export default defineComponent({
  name: "CmpResultadoMejorada",
  components: { VAviso, VButton, VIcon },
  props: {
    resultado: { type: Array as PropType<string[]>, required: true },
  },
  emits: {
    copiar: () => true,
    probar: () => true,
  },
  setup() {
    const PREFIX = "cmp-resultado-mejorada";

    return { PREFIX };
  },
});
