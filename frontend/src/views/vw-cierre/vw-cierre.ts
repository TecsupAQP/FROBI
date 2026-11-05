import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpCierre from "@/components/business/cmp-cierre/cmp-cierre.vue";

export default defineComponent({
  name: "VwCierre",
  components: { CmpLayoutPagina, CmpCierre },
  setup() {
    return {};
  },
});
