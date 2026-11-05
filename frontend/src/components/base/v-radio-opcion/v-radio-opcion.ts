import { defineComponent, useModel } from "vue";

export default defineComponent({
  name: "VRadioOpcion",
  props: {
    nombre: { type: String, required: true },
    valor: { type: String, required: true },
    error: { type: Boolean, default: false },
    descripcion: { type: String, default: undefined },
    modelValue: { type: String, default: "" },
  },
  emits: {
    "update:modelValue": (_valor: string) => true,
  },
  setup(props) {
    const modelo = useModel(props, "modelValue");

    const PREFIX = "v-radio-opcion";

    return { PREFIX, modelo };
  },
});
