import { defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { NombreIcono } from "@/constants/iconos.constant";

export default defineComponent({
  name: "VEstadoVacio",
  components: { VIcon },
  props: {
    icono: { type: String as PropType<NombreIcono>, required: true },
    titulo: { type: String, required: true },
    texto: { type: String, required: true },
  },
  setup() {
    const PREFIX = "v-estado-vacio";

    return { PREFIX };
  },
});
