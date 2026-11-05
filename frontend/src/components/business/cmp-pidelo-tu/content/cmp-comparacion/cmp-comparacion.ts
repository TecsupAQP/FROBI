import { computed, defineComponent, type PropType } from "vue";
import VChipPieza from "@/components/base/v-chip-pieza/v-chip-pieza.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VTarjetaPieza from "@/components/base/v-tarjeta-pieza/v-tarjeta-pieza.vue";
import type { InstruccionMejorada, PromptScore } from "@/core/shared/domain/view/prompt-score.view";

export default defineComponent({
  name: "CmpComparacion",
  components: { VChipPieza, VIcon, VTarjetaPieza },
  props: {
    evaluacion: { type: Object as PropType<PromptScore>, required: true },
    mejorada: { type: Object as PropType<InstruccionMejorada>, required: true },
  },
  setup(props) {
    const PREFIX = "cmp-comparacion";

    const faltantes = computed(() => props.evaluacion.piezas.filter((item) => !item.presente));

    return { PREFIX, faltantes };
  },
});
