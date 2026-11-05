import { defineComponent, type PropType } from "vue";
import logoIcono from "@/assets/resources/images/logo-frobi-icono.svg";

// Mientras FROBI piensa o consulta datos, antes de que llegue el texto.
export default defineComponent({
  name: "CmpEscribiendo",
  props: {
    estado: { type: String as PropType<string | null>, default: null },
  },
  setup() {
    const PREFIX = "cmp-escribiendo";

    return { PREFIX, logoIcono };
  },
});
