import { defineComponent, type PropType } from "vue";
import type { ContenidoLecturaFacil } from "@/core/shared/domain/view/adaptation.view";

export default defineComponent({
  name: "CmpLecturaFacil",
  props: {
    contenido: { type: Object as PropType<ContenidoLecturaFacil>, required: true },
  },
  setup() {
    const PREFIX = "cmp-lectura-facil";

    return { PREFIX };
  },
});
