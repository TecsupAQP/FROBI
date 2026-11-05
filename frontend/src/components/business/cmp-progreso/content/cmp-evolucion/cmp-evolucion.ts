import { computed, defineComponent, type PropType } from "vue";

export default defineComponent({
  name: "CmpEvolucion",
  props: {
    intentos: { type: Array as PropType<number[]>, required: true },
    maximo: { type: Number, default: 4 },
  },
  setup(props) {
    const PREFIX = "cmp-evolucion";

    // Geometría del gráfico en Figma: 170 px de alto, línea base en 150 y techo en 20.
    const ALTO = 170;

    const BASE = 150;

    const TECHO = 20;

    const GUIAS = [TECHO, (BASE + TECHO) / 2, BASE];

    const puntos = computed(() =>
      props.intentos.map((valor, indice) => ({
        xPorcentaje: ((indice + 0.5) / props.intentos.length) * 100,
        xSvg: indice * 100 + 50,
        y: BASE - (valor / props.maximo) * (BASE - TECHO),
      })),
    );

    const puntosSvg = computed(() => puntos.value.map((punto) => `${punto.xSvg},${punto.y}`).join(" "));

    return { PREFIX, ALTO, GUIAS, puntos, puntosSvg };
  },
});
