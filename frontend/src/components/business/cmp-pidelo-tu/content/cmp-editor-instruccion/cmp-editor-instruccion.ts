import { defineComponent, useModel } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";

export default defineComponent({
  name: "CmpEditorInstruccion",
  components: { VButton, VCargando },
  props: {
    etiqueta: { type: String, required: true },
    piezasEscritas: { type: Number, required: true },
    totalPiezas: { type: Number, default: 4 },
    puedePedir: { type: Boolean, default: false },
    ocupado: { type: Boolean, default: false },
    compacto: { type: Boolean, default: false },
    modelValue: { type: String, default: "" },
  },
  emits: {
    pedir: () => true,
    "update:modelValue": (_valor: string) => true,
  },
  setup(props) {
    const modelo = useModel(props, "modelValue");

    const PREFIX = "cmp-editor-instruccion";

    return { PREFIX, modelo };
  },
});
