import { defineComponent } from "vue";
import CmpBarraSuperior from "@/components/common/cmp-barra-superior/cmp-barra-superior.vue";
import CmpRecorrido from "@/components/common/cmp-recorrido/cmp-recorrido.vue";

export default defineComponent({
  name: "CmpLayoutPagina",
  components: { CmpBarraSuperior, CmpRecorrido },
  setup() {
    const PREFIX = "cmp-layout-pagina";

    return { PREFIX };
  },
});
