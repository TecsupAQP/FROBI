import { defineComponent } from "vue";
import CmpLayoutPresentacion from "@/components/common/cmp-layout-presentacion/cmp-layout-presentacion.vue";
import CmpPersonas from "@/components/business/cmp-personas/cmp-personas.vue";

export default defineComponent({
  name: "VwPersonas",
  components: { CmpLayoutPresentacion, CmpPersonas },
  setup() {
    return {};
  },
});
