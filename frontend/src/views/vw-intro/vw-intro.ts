import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpIntro from "@/components/business/cmp-intro/cmp-intro.vue";

export default defineComponent({
  name: "VwIntro",
  components: { CmpLayoutPagina, CmpIntro },
  setup() {
    return {};
  },
});
