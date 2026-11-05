import { defineComponent, type PropType } from "vue";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";

// Vista previa del PDF que subió la persona (guardado en R2, se abre con un enlace temporal).
export default defineComponent({
  name: "CmpDocumentoOriginal",
  components: { VAviso, VCargando, VIcon },
  props: {
    titulo: { type: String, required: true },
    abierto: { type: Boolean, required: true },
    url: { type: String as PropType<string | null>, default: null },
    error: { type: Boolean, default: false },
  },
  emits: {
    alternar: () => true,
  },
  setup() {
    const PREFIX = "cmp-documento-original";

    return { PREFIX };
  },
});
