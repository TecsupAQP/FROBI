import { defineComponent, useModel } from "vue";

export default defineComponent({
  name: "VSwitch",
  props: {
    id: { type: String, required: true },
    etiqueta: { type: String, required: true },
    modelValue: { type: Boolean, default: false },
  },
  emits: {
    "update:modelValue": (_valor: boolean) => true,
  },
  setup(props) {
    const modelo = useModel(props, "modelValue");

    const PREFIX = "v-switch";

    return { PREFIX, modelo };
  },
});
