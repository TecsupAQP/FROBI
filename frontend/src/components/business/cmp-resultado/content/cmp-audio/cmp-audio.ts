import { defineComponent, onBeforeUnmount, ref, watch, type PropType } from "vue";
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

    // La voz es la del navegador (Web Speech API): se lee frase por frase y se resalta la actual.
    const vozDisponible = typeof window !== "undefined" && "speechSynthesis" in window;

    const posicion = ref(props.contenido.posicionSegundos);

    const fraseActual = ref(props.contenido.fraseActual);

    const reproduciendo = ref(false);

    const velocidad = ref<(typeof VELOCIDADES)[number]>(1);

    const formatearTiempo = (segundos: number) =>
      `${Math.floor(segundos / 60)}:${String(Math.floor(segundos % 60)).padStart(2, "0")}`;

    // Segundo en que empieza cada frase, repartiendo la duración según sus palabras.
    const palabras = props.contenido.frases.map((frase) => frase.split(/\s+/).length);
    const totalPalabras = palabras.reduce((suma, valor) => suma + valor, 0) || 1;
    const inicioDe = (indice: number) =>
      (palabras.slice(0, indice).reduce((suma, valor) => suma + valor, 0) / totalPalabras) *
      props.contenido.duracionSegundos;
    const fraseEn = (segundos: number) => {
      const indice = props.contenido.frases.findIndex((_frase, i) => inicioDe(i + 1) > segundos);
      return indice === -1 ? props.contenido.frases.length - 1 : indice;
    };

    const detener = () => {
      if (vozDisponible) window.speechSynthesis.cancel();
    };

    const leerDesde = (indice: number) => {
      const frase = props.contenido.frases[indice];
      if (!frase || !vozDisponible) {
        reproduciendo.value = false;
        return;
      }
      fraseActual.value = indice;
      posicion.value = inicioDe(indice);
      const lectura = new SpeechSynthesisUtterance(frase);
      lectura.lang = "es-PE";
      lectura.rate = velocidad.value;
      lectura.onend = () => {
        if (!reproduciendo.value) return;
        if (indice + 1 >= props.contenido.frases.length) {
          reproduciendo.value = false;
          posicion.value = props.contenido.duracionSegundos;
          return;
        }
        leerDesde(indice + 1);
      };
      window.speechSynthesis.speak(lectura);
    };

    const alternar = () => {
      reproduciendo.value = !reproduciendo.value;
      detener();
      if (reproduciendo.value) {
        const desde = posicion.value >= props.contenido.duracionSegundos ? 0 : fraseActual.value;
        leerDesde(desde);
      }
    };

    const mover = (delta: number) => {
      posicion.value = Math.min(props.contenido.duracionSegundos, Math.max(0, posicion.value + delta));
      fraseActual.value = fraseEn(posicion.value);
      if (reproduciendo.value) {
        detener();
        leerDesde(fraseActual.value);
      }
    };

    const cambiarVelocidad = () => {
      const indice = VELOCIDADES.indexOf(velocidad.value);
      velocidad.value = VELOCIDADES[(indice + 1) % VELOCIDADES.length] ?? 1;
    };

    // Al cambiar de velocidad, la frase actual se vuelve a leer con la nueva.
    watch(velocidad, () => {
      if (!reproduciendo.value) return;
      detener();
      leerDesde(fraseActual.value);
    });

    onBeforeUnmount(() => {
      reproduciendo.value = false;
      detener();
    });

    return {
      PREFIX,
      vozDisponible,
      posicion,
      fraseActual,
      reproduciendo,
      velocidad,
      formatearTiempo,
      alternar,
      mover,
      cambiarVelocidad,
    };
  },
});
