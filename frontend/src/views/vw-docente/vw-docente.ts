import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpDocente from "@/components/business/cmp-docente/cmp-docente.vue";

export default defineComponent({
  name: "VwDocente",
  components: { CmpLayoutPagina, CmpDocente },
  setup() {
    return {};
  },
});
