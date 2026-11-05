import { defineComponent, type PropType } from "vue";
import VProgressBar from "@/components/base/v-progress-bar/v-progress-bar.vue";

export default defineComponent({
  name: "VBarraDato",
  components: { VProgressBar },
  props: {
    etiqueta: { type: String, required: true },
    valor: { type: Number, required: true },
    maximo: { type: Number, default: 100 },
    valorTexto: { type: String, required: true },
    tono: { type: String as PropType<"marca" | "error" | "aviso">, default: "marca" },
  },
  setup() {
    const PREFIX = "v-barra-dato";

    return { PREFIX };
  },
});
