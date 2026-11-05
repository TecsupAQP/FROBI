import { defineComponent, type PropType } from "vue";
import type { RouteLocationRaw } from "vue-router";
import VIcon from "@/components/base/v-icon/v-icon.vue";

export default defineComponent({
  name: "CmpEncabezadoPagina",
  components: { VIcon },
  props: {
    titulo: { type: String, required: true },
    antetitulo: { type: String, default: undefined },
    descripcion: { type: String, default: undefined },
    volver: { type: Object as PropType<{ texto: string; destino: RouteLocationRaw }>, default: undefined },
  },
  setup() {
    const PREFIX = "cmp-encabezado-pagina";

    return { PREFIX };
  },
});
