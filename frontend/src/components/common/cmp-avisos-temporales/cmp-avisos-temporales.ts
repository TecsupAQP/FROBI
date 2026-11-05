import { defineComponent } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import useCmpAvisos from "@/composables/common/cmp-avisos/cmp-avisos.composable";

export default defineComponent({
  name: "CmpAvisosTemporales",
  components: { VIcon },
  setup() {
    const PREFIX = "cmp-avisos-temporales";

    const { avisos, quitarAviso } = useCmpAvisos();

    return { PREFIX, avisos, quitarAviso };
  },
});
