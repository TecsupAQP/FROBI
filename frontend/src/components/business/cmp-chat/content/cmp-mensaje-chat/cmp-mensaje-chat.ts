import { defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import logoIcono from "@/assets/resources/images/logo-frobi-icono.svg";
import type { LineaChat } from "@/core/shared/domain/view/asistente.view";

export default defineComponent({
  name: "CmpMensajeChat",
  components: { VIcon },
  props: {
    linea: { type: Object as PropType<LineaChat>, required: true },
  },
  setup() {
    const PREFIX = "cmp-mensaje-chat";

    return { PREFIX, logoIcono };
  },
});
