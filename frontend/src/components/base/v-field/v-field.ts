import { computed, defineComponent, useModel, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";

export default defineComponent({
  name: "VField",
  components: { VIcon },
  props: {
    id: { type: String, required: true },
    etiqueta: { type: String, required: true },
    placeholder: { type: String, default: undefined },
    tipo: { type: String as PropType<"text" | "search">, default: "text" },
    ayuda: { type: String, default: undefined },
    error: { type: String, default: undefined },
    multilinea: { type: Boolean, default: false },
    filas: { type: Number, default: 4 },
    autocompletar: { type: String, default: "off" },
    tamano: { type: String as PropType<"normal" | "grande">, default: "normal" },
    modelValue: { type: String, default: "" },
  },
  emits: {
    "update:modelValue": (_valor: string) => true,
  },
  setup(props) {
    const modelo = useModel(props, "modelValue");

    const PREFIX = "v-field";

    const descripcionId = computed(() => {
      if (props.error) return `${props.id}-error`;
      return props.ayuda ? `${props.id}-ayuda` : undefined;
    });

    return { PREFIX, descripcionId, modelo };
  },
});
