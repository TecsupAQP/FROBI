import { defineComponent, type PropType } from "vue";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import type { ContenidoMapaVisual } from "@/core/shared/domain/view/adaptation.view";

export default defineComponent({
  name: "CmpMapaVisual",
  components: { VAviso },
  props: {
    contenido: { type: Object as PropType<ContenidoMapaVisual>, required: true },
  },
  setup() {
    const PREFIX = "cmp-mapa-visual";

    return { PREFIX };
  },
});
