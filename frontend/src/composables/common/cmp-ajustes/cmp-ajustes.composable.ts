import { storeToRefs } from "pinia";
import { useCmpAjustesStore } from "@/store/common/cmp-ajustes/cmp-ajustes.store";

function useCmpAjustes() {
  const store = useCmpAjustesStore();
  const { ajustes, cargado, idiomas } = storeToRefs(store);

  return {
    ajustes,
    cargado,
    idiomas,

    activarVarios: store.activarVarios,
    alternar: store.alternar,
    cargar: store.cargar,
  };
}

export default useCmpAjustes;
