import { storeToRefs } from "pinia";
import { useCmpProgresoStore } from "@/store/business/cmp-progreso/cmp-progreso.store";

function useCmpProgreso() {
  const store = useCmpProgresoStore();
  const { estado, progreso } = storeToRefs(store);

  return {
    estado,
    progreso,

    cargar: store.cargar,
  };
}

export default useCmpProgreso;
