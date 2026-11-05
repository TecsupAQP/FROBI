import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpPideloTu from "@/components/business/cmp-pidelo-tu/cmp-pidelo-tu.vue";

export default defineComponent({
  name: "VwPideloTu",
  components: { CmpLayoutPagina, CmpPideloTu },
  setup() {
    return {};
  },
});
