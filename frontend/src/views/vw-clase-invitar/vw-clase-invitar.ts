import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpClaseInvitar from "@/components/business/cmp-clase/cmp-clase-invitar.vue";

export default defineComponent({
  name: "VwClaseInvitar",
  components: { CmpLayoutPagina, CmpClaseInvitar },
  setup() {
    return {};
  },
});
