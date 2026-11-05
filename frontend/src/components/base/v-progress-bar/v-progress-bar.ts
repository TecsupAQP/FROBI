import { computed, defineComponent, type PropType } from "vue";

export default defineComponent({
  name: "VProgressBar",
  props: {
    valor: { type: Number, required: true },
    maximo: { type: Number, default: 100 },
    etiqueta: { type: String, required: true },
    textoValor: { type: String, default: undefined },
    tono: { type: String as PropType<"marca" | "claro" | "exito">, default: "marca" },
  },
  setup(props) {
    const PREFIX = "v-progress-bar";

    const valorSeguro = computed(() => Math.min(props.maximo, Math.max(0, props.valor)));

    return { PREFIX, valorSeguro };
  },
});
