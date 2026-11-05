import { defineComponent, useModel, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { NombreIcono } from "@/constants/iconos.constant";

export default defineComponent({
  name: "VCasilla",
  components: { VIcon },
  props: {
    descripcion: { type: String, default: undefined },
    icono: { type: String as PropType<NombreIcono>, default: undefined },
    modelValue: { type: Boolean, default: false },
  },
  emits: {
    "update:modelValue": (_valor: boolean) => true,
  },
  setup(props) {
    const modelo = useModel(props, "modelValue");

    const PREFIX = "v-casilla";

    return { PREFIX, modelo };
  },
});
