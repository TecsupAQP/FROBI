import { defineComponent } from "vue";
import VChipPieza from "@/components/base/v-chip-pieza/v-chip-pieza.vue";
import VLogo from "@/components/base/v-logo/v-logo.vue";
import type { PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";

export default defineComponent({
  name: "CmpPanelMarca",
  components: { VChipPieza, VLogo },
  setup() {
    const PREFIX = "cmp-panel-marca";

    // Ejemplo fijo de la pantalla de bienvenida (texto de marketing, no viene del backend).
    const receta: PiezaInstruccion[] = [
      { pieza: "contexto", texto: "Soy estudiante de primer ciclo de Mecatrónica." },
      { pieza: "objetivo", texto: "Necesito elegir un sensor para una faja." },
      { pieza: "nivel", texto: "Explícalo sin fórmulas, con palabras simples." },
      { pieza: "formato", texto: "Usa un ejemplo de una línea de embotellado." },
    ];

    return { PREFIX, receta };
  },
});
