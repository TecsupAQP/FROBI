import { defineComponent, type PropType } from "vue";
import VBarraDato from "@/components/base/v-barra-dato/v-barra-dato.vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import { ALERTA_ALUMNO } from "@/constants/clase.constant";
import type { Clase } from "@/core/shared/domain/view/clase.view";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "CmpMiClase",
  components: { VBarraDato, VButton, VChip },
  props: {
    clase: { type: Object as PropType<Clase>, required: true },
  },
  setup() {
    const PREFIX = "cmp-mi-clase";

    return { ALERTA_ALUMNO, RutaEnum, PREFIX };
  },
});
