import { defineComponent, ref, type PropType } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { MaterialClase } from "@/core/shared/domain/view/clase.view";

const FECHA = new Intl.DateTimeFormat("es-PE", { day: "numeric", month: "long" });

export default defineComponent({
  name: "CmpContenidoClase",
  components: { VButton, VIcon },
  props: {
    materiales: { type: Array as PropType<MaterialClase[]>, required: true },
    subiendo: { type: Boolean, default: false },
    error: { type: String as PropType<string | null>, default: null },
  },
  emits: {
    subir: (_archivo: File) => true,
  },
  setup(_props, { emit }) {
    const PREFIX = "cmp-contenido-clase";

    const selector = ref<HTMLInputElement | null>(null);

    const abrirSelector = () => selector.value?.click();

    const alElegir = (evento: Event) => {
      const entrada = evento.target as HTMLInputElement;
      const archivo = entrada.files?.[0];
      if (archivo) emit("subir", archivo);
      entrada.value = "";
    };

    const formatearFecha = (fecha: string) => FECHA.format(new Date(fecha));

    return { PREFIX, selector, abrirSelector, alElegir, formatearFecha };
  },
});
