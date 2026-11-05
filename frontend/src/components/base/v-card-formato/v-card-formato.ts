import { defineComponent, type PropType } from "vue";
import { RouterLink, type RouteLocationRaw } from "vue-router";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { DefinicionFormato } from "@/constants/formatos.constant";
import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";

export default defineComponent({
  name: "VCardFormato",
  components: { VIcon },
  props: {
    formato: { type: Object as PropType<DefinicionFormato>, required: true },
    destino: { type: [String, Object] as PropType<RouteLocationRaw>, default: undefined },
    atenuada: { type: Boolean, default: false },
    elegida: { type: Boolean, default: false },
  },
  emits: {
    elegir: (_formato: FormatoId) => true,
  },
  setup() {
    const PREFIX = "v-card-formato";

    return { RouterLink, PREFIX };
  },
});
