import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpAjustes from "@/components/business/cmp-ajustes/cmp-ajustes.vue";

export default defineComponent({
  name: "VwAjustes",
  components: { CmpLayoutPagina, CmpAjustes },
  setup() {
    return {};
  },
});
