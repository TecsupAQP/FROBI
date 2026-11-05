import { computed, defineComponent, type PropType } from "vue";
import VCargando from "@/components/base/v-cargando/v-cargando.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import type { Pregunta } from "@/core/shared/domain/view/pregunta.view";

export default defineComponent({
  name: "CmpPregunta",
  components: { VCargando, VIcon },
  props: {
    pregunta: { type: Object as PropType<Pregunta>, required: true },
    elegida: { type: String as PropType<string | null>, default: null },
    revisando: { type: String as PropType<string | null>, default: null },
    acerto: { type: Boolean, required: true },
  },
  emits: {
    responder: (_opcionId: string) => true,
  },
  setup(props) {
    const PREFIX = "cmp-pregunta";

    const respondida = computed(() => props.elegida !== null);

    const bloqueada = computed(() => respondida.value || props.revisando !== null);

    const claseOpcion = (opcionId: string) => {
      if (props.revisando !== null) {
        return opcionId === props.revisando ? `${PREFIX}__opcion--revisando` : `${PREFIX}__opcion--atenuada`;
      }
      if (opcionId !== props.elegida) return "";
      return props.acerto ? `${PREFIX}__opcion--correcta` : `${PREFIX}__opcion--incorrecta`;
    };

    return { PREFIX, respondida, bloqueada, claseOpcion };
  },
});
