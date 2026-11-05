import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpChat from "@/components/business/cmp-chat/cmp-chat.vue";

export default defineComponent({
  name: "VwChat",
  components: { CmpLayoutPagina, CmpChat },
  setup() {
    return {};
  },
});
