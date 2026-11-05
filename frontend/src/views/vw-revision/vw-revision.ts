import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpRevision from "@/components/business/cmp-revision/cmp-revision.vue";

export default defineComponent({
  name: "VwRevision",
  components: { CmpLayoutPagina, CmpRevision },
  setup() {
    return {};
  },
});
