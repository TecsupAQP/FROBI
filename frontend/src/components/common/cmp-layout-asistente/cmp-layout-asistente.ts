import { defineComponent } from "vue";
import VLogo from "@/components/base/v-logo/v-logo.vue";

export default defineComponent({
  name: "CmpLayoutAsistente",
  components: { VLogo },
  props: {
    textoOmitir: { type: String, default: "Omitir configuración" },
  },
  emits: {
    omitir: () => true,
  },
  setup() {
    const PREFIX = "cmp-layout-asistente";

    return { PREFIX };
  },
});
