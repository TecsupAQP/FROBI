import { storeToRefs } from "pinia";
import { useCmpHerramientasStore } from "@/store/business/cmp-herramientas/cmp-herramientas.store";

function useCmpHerramientas() {
  const store = useCmpHerramientasStore();
  const { necesidad, nombreNecesidad, otras, recomendacion, recomendada } = storeToRefs(store);

  return {
    necesidad,
    nombreNecesidad,
    otras,
    recomendacion,
    recomendada,

    cargar: store.cargar,
    elegirNecesidad: store.elegirNecesidad,
  };
}

export default useCmpHerramientas;
