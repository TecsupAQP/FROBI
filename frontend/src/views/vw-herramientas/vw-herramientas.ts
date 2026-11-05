import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpHerramientas from "@/components/business/cmp-herramientas/cmp-herramientas.vue";

export default defineComponent({
  name: "VwHerramientas",
  components: { CmpLayoutPagina, CmpHerramientas },
  setup() {
    return {};
  },
});
