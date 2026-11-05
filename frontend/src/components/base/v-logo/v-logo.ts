import { defineComponent, type PropType } from "vue";
import logoHorizontal from "@/assets/resources/images/logo-frobi-horizontal.svg";
import logoIcono from "@/assets/resources/images/logo-frobi-icono.svg";

export default defineComponent({
  name: "VLogo",
  props: {
    variante: { type: String as PropType<"horizontal" | "icono" | "inverso">, default: "horizontal" },
    alto: { type: Number, default: 40 },
  },
  setup() {
    const PREFIX = "v-logo";

    // Proporciones de los símbolos de Figma (Marca · FROBI): 510 × 230 y 225 × 220.
    const PROPORCION_HORIZONTAL = 510 / 230;

    const PROPORCION_ICONO = 225 / 220;

    return { logoHorizontal, logoIcono, PREFIX, PROPORCION_HORIZONTAL, PROPORCION_ICONO };
  },
});
