import { defineComponent } from "vue";
import VLogo from "@/components/base/v-logo/v-logo.vue";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpLayoutPresentacion",
  components: { VLogo },
  setup() {
    const PREFIX = "cmp-layout-presentacion";

    return { RutaEnum, PREFIX };
  },
});
