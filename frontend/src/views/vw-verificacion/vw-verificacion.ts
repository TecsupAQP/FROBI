import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpVerificacion from "@/components/business/cmp-verificacion/cmp-verificacion.vue";

export default defineComponent({
  name: "VwVerificacion",
  components: { CmpLayoutPagina, CmpVerificacion },
  setup() {
    return {};
  },
});
