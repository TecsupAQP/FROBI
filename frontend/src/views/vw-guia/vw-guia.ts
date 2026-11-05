import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpGuia from "@/components/business/cmp-guia/cmp-guia.vue";

export default defineComponent({
  name: "VwGuia",
  components: { CmpLayoutPagina, CmpGuia },
  setup() {
    return {};
  },
});
