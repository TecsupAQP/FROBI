import { storeToRefs } from "pinia";
import { useCmpGuiaStore } from "@/store/business/cmp-guia/cmp-guia.store";

function useCmpGuia() {
  const store = useCmpGuiaStore();
  const { formatoAdaptando, guia, tardaMucho, temaAbierto } = storeToRefs(store);

  return {
    formatoAdaptando,
    guia,
    tardaMucho,
    temaAbierto,

    adaptar: store.adaptar,
    alternarTema: store.alternarTema,
    cargarGuia: store.cargarGuia,
  };
}

export default useCmpGuia;
