import { defineComponent, type PropType } from "vue";
import { RouterLink, type RouteLocationRaw } from "vue-router";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { NombreIcono } from "@/constants/iconos.constant";

export default defineComponent({
  name: "VButton",
  components: { VIcon },
  props: {
    variante: {
      type: String as PropType<"primario" | "secundario" | "cerrar" | "texto">,
      default: "primario",
    },
    tipo: { type: String as PropType<"button" | "submit">, default: "button" },
    icono: { type: String as PropType<NombreIcono>, default: undefined },
    iconoFin: { type: String as PropType<NombreIcono>, default: undefined },
    destino: { type: [String, Object] as PropType<RouteLocationRaw>, default: undefined },
    bloque: { type: Boolean, default: false },
    deshabilitado: { type: Boolean, default: false },
    etiqueta: { type: String, default: undefined },
  },
  emits: {
    click: (_evento: MouseEvent) => true,
  },
  setup() {
    const PREFIX = "v-button";

    return { RouterLink, PREFIX };
  },
});
