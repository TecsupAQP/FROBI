import { defineComponent, type PropType } from "vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import { ESTADO_ALUMNO } from "@/constants/clase.constant";
import type { AlumnoClase } from "@/core/shared/domain/view/clase.view";

export default defineComponent({
  name: "CmpAlumnoItem",
  components: { VChip },
  props: {
    alumno: { type: Object as PropType<AlumnoClase>, required: true },
  },
  setup() {
    const PREFIX = "cmp-alumno-item";

    return { ESTADO_ALUMNO, PREFIX };
  },
});
