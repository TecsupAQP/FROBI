import { storeToRefs } from "pinia";
import { useCmpCierreStore } from "@/store/business/cmp-cierre/cmp-cierre.store";

function useCmpCierre() {
  const store = useCmpCierreStore();
  const { resumen } = storeToRefs(store);

  return {
    resumen,

    cargar: store.cargar,
  };
}

export default useCmpCierre;
