import { defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { NombreIcono } from "@/constants/iconos.constant";

export default defineComponent({
  name: "VOpcionTarjeta",
  components: { VIcon },
  props: {
    nombre: { type: String, required: true },
    titulo: { type: String, required: true },
    descripcion: { type: String, default: undefined },
    icono: { type: String as PropType<NombreIcono>, default: undefined },
    elegida: { type: Boolean, default: false },
    multiple: { type: Boolean, default: false },
    disposicion: { type: String as PropType<"amplia" | "compacta">, default: "amplia" },
  },
  emits: {
    elegir: () => true,
  },
  setup() {
    const PREFIX = "v-opcion-tarjeta";

    return { PREFIX };
  },
});
