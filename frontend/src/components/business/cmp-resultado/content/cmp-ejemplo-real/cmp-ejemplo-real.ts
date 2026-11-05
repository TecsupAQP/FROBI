import { defineComponent, type PropType } from "vue";
import VAviso from "@/components/base/v-aviso/v-aviso.vue";
import type { ContenidoEjemploReal } from "@/core/shared/domain/view/adaptation.view";
import imgCampo from "@/assets/resources/images/campo-electromagnetico.png";
import imgLuz from "@/assets/resources/images/luz-senal.svg";
import imgRodillo from "@/assets/resources/images/rodillo.svg";

export default defineComponent({
  name: "CmpEjemploReal",
  components: { VAviso },
  props: {
    contenido: { type: Object as PropType<ContenidoEjemploReal>, required: true },
  },
  setup() {
    const PREFIX = "cmp-ejemplo-real";

    const POSICIONES_BOTELLA = ["antes", "detectada", "despues"] as const;

    return { imgCampo, imgLuz, imgRodillo, PREFIX, POSICIONES_BOTELLA };
  },
});
