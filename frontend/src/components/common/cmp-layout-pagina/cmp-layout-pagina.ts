import { defineComponent } from "vue";
import CmpBarraSuperior from "@/components/common/cmp-barra-superior/cmp-barra-superior.vue";

export default defineComponent({
  name: "CmpLayoutPagina",
  components: { CmpBarraSuperior },
  setup() {
    const PREFIX = "cmp-layout-pagina";

    return { PREFIX };
  },
});
