import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpRol from "@/components/business/cmp-rol/cmp-rol.vue";

export default defineComponent({
  name: "VwRol",
  components: { CmpLayoutPagina, CmpRol },
  setup() {
    return {};
  },
});
