import { computed, defineComponent, type PropType } from "vue";
import { ICONOS, type NombreIcono } from "@/constants/iconos.constant";

export default defineComponent({
  name: "VIcon",
  props: {
    nombre: { type: String as PropType<NombreIcono>, required: true },
    tamano: { type: Number, default: 24 },
    etiqueta: { type: String, default: undefined },
  },
  setup(props) {
    const PREFIX = "v-icon";

    const definicion = computed(() => ICONOS[props.nombre]);

    return { PREFIX, definicion };
  },
});
