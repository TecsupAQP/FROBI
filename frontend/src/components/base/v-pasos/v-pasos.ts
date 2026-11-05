import { defineComponent } from "vue";

export default defineComponent({
  name: "VPasos",
  props: {
    actual: { type: Number, required: true },
    total: { type: Number, required: true },
    nota: { type: String, default: undefined },
  },
  setup() {
    const PREFIX = "v-pasos";

    return { PREFIX };
  },
});
