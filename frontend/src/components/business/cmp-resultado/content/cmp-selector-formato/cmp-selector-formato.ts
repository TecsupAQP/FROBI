import { defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import { FORMATOS } from "@/constants/formatos.constant";
import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpSelectorFormato",
  components: { VIcon },
  props: {
    activo: { type: String as PropType<FormatoId>, required: true },
  },
  setup() {
    const PREFIX = "cmp-selector-formato";

    return { FORMATOS, RutaEnum, PREFIX };
  },
});
