import { storeToRefs } from "pinia";
import { useCmpResultadoStore } from "@/store/business/cmp-resultado/cmp-resultado.store";

function useCmpResultado() {
  const store = useCmpResultadoStore();
  const { adaptacion, estado, estaCargando, formatoActual, recetaDesplegada, usaRespaldo } =
    storeToRefs(store);

  return {
    adaptacion,
    estaCargando,
    estado,
    formatoActual,
    recetaDesplegada,
    usaRespaldo,

    alternarReceta: store.alternarReceta,
    cargarAdaptacion: store.cargarAdaptacion,
  };
}

export default useCmpResultado;
