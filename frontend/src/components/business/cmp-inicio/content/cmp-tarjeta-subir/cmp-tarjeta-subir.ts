import { defineComponent } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";

export default defineComponent({
  name: "CmpTarjetaSubir",
  components: { VButton },
  emits: {
    subir: () => true,
  },
  setup() {
    const PREFIX = "cmp-tarjeta-subir";

    return { PREFIX };
  },
});
