import { defineComponent, ref, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import useVoz from "@/composables/common/voz/voz.composable";

export default defineComponent({
  name: "VBotonEscuchar",
  components: { VIcon },
  props: {
    lectura: { type: String, required: true },
    texto: { type: String, default: "Escuchar esta pregunta" },
    tono: { type: String as PropType<"borde" | "suave">, default: "borde" },
  },
  setup(props) {
    const PREFIX = "v-boton-escuchar";

    const { disponible, hablando, detener, leer } = useVoz();

    const sinVoz = ref(false);

    const alternar = () => {
      if (hablando.value) {
        detener();
        return;
      }
      sinVoz.value = !disponible || !leer(props.lectura);
    };

    return { PREFIX, hablando, leer, sinVoz, alternar };
  },
});
