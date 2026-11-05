import { computed, defineComponent, type PropType } from "vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VSelect from "@/components/base/v-select/v-select.vue";
import type { Tema } from "@/core/shared/domain/view/material.view";

const LARGO_RESUMEN = 160;

// Qué tema de la guía se va a estudiar: cada formato se arma solo con ese tema.
export default defineComponent({
  name: "CmpElegirTema",
  components: { VIcon, VSelect },
  props: {
    temas: { type: Array as PropType<Tema[]>, required: true },
    elegido: { type: Object as PropType<Tema>, required: true },
  },
  emits: {
    elegir: (_temaId: string) => true,
  },
  setup(props, { emit }) {
    const PREFIX = "cmp-elegir-tema";

    const indice = computed(() =>
      Math.max(
        0,
        props.temas.findIndex((tema) => tema.id === props.elegido.id),
      ),
    );
    const actual = computed(() => props.temas[indice.value] ?? props.elegido);

    const resumen = computed(() => {
      const texto = actual.value.textoOriginal;
      return texto.length > LARGO_RESUMEN ? `${texto.slice(0, LARGO_RESUMEN).trimEnd()}…` : texto;
    });

    const opciones = computed(() =>
      props.temas.map((tema) => ({
        id: tema.id,
        nombre: `${tema.numero}. ${tema.titulo}${tema.paginas ? ` · ${tema.paginas}` : ""}`,
      })),
    );

    const mover = (paso: number) => {
      const siguiente = props.temas[indice.value + paso];
      if (siguiente) emit("elegir", siguiente.id);
    };

    return { PREFIX, actual, indice, opciones, resumen, mover };
  },
});
