import { defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { Escalon, EstadoEscalon } from "@/core/shared/domain/view/ayuda.view";

export default defineComponent({
  name: "CmpEscalon",
  components: { VIcon },
  props: {
    escalon: { type: Object as PropType<Escalon>, required: true },
    numero: { type: Number, required: true },
    estado: { type: String as PropType<EstadoEscalon>, required: true },
    textoBloqueo: { type: String, default: "" },
  },
  setup() {
    const PREFIX = "cmp-escalon";

    // El estado también se dice con texto (para lectores de pantalla), no solo con color e icono.
    const ESTADO_TEXTO: Record<EstadoEscalon, string> = {
      hecho: "hecho",
      activo: "estás aquí",
      abierto: "abierto",
      bloqueado: "bloqueado",
    };

    return { PREFIX, ESTADO_TEXTO };
  },
});
