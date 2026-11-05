import { defineComponent } from "vue";
import CmpLayoutPresentacion from "@/components/common/cmp-layout-presentacion/cmp-layout-presentacion.vue";
import CmpComoSeUsa from "@/components/business/cmp-como-se-usa/cmp-como-se-usa.vue";

export default defineComponent({
  name: "VwComoSeUsa",
  components: { CmpLayoutPresentacion, CmpComoSeUsa },
  setup() {
    return {};
  },
});
