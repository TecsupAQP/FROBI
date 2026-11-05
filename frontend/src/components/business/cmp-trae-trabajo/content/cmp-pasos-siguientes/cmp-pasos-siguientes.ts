import { defineComponent } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";

export default defineComponent({
  name: "CmpPasosSiguientes",
  components: { VIcon },
  setup() {
    const PREFIX = "cmp-pasos-siguientes";

    const PASOS = [
      "Ves tu trabajo marcado por secciones.",
      "Revisas lo que conviene verificar.",
      "Eliges una herramienta y escribes tu instrucción.",
      "Adaptas el trabajo al formato que necesitas.",
    ];

    return { PREFIX, PASOS };
  },
});
