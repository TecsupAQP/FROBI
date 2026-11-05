import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpClaseNueva from "@/components/business/cmp-clase/cmp-clase-nueva.vue";

export default defineComponent({
  name: "VwClaseNueva",
  components: { CmpLayoutPagina, CmpClaseNueva },
  setup() {
    return {};
  },
});
