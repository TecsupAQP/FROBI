import { defineComponent, ref, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VProgressBar from "@/components/base/v-progress-bar/v-progress-bar.vue";
import type { ContenidoAudio } from "@/core/shared/domain/view/adaptation.view";

export default defineComponent({
  name: "CmpAudio",
  components: { VIcon, VProgressBar },
  props: {
    contenido: { type: Object as PropType<ContenidoAudio>, required: true },
  },
  setup(props) {
    const PREFIX = "cmp-audio";

    const VELOCIDADES = [1, 1.25, 1.5, 0.75] as const;

    // Reproductor simulado: solo mueve la barra, no reproduce sonido.
    const posicion = ref(props.contenido.posicionSegundos);

    const reproduciendo = ref(false);

    const velocidad = ref<(typeof VELOCIDADES)[number]>(1);

    const formatearTiempo = (segundos: number) =>
      `${Math.floor(segundos / 60)}:${String(Math.floor(segundos % 60)).padStart(2, "0")}`;

    const mover = (delta: number) => {
      posicion.value = Math.min(props.contenido.duracionSegundos, Math.max(0, posicion.value + delta));
    };

    const cambiarVelocidad = () => {
      const indice = VELOCIDADES.indexOf(velocidad.value);
      velocidad.value = VELOCIDADES[(indice + 1) % VELOCIDADES.length] ?? 1;
    };

    return { PREFIX, posicion, reproduciendo, velocidad, formatearTiempo, mover, cambiarVelocidad };
  },
});
