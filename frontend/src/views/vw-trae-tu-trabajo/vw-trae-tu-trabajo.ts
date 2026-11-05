import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpTraeTrabajo from "@/components/business/cmp-trae-trabajo/cmp-trae-trabajo.vue";

export default defineComponent({
  name: "VwTraeTuTrabajo",
  components: { CmpLayoutPagina, CmpTraeTrabajo },
  setup() {
    return {};
  },
});
