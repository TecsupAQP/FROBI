import { storeToRefs } from "pinia";
import { useCmpGuiaStore } from "@/store/business/cmp-guia/cmp-guia.store";

function useCmpGuia() {
  const store = useCmpGuiaStore();
  const {
    documentoAbierto,
    documentoError,
    documentoUrl,
    formatoAdaptando,
    guia,
    tardaMucho,
    temaAbierto,
    temaElegido,
  } = storeToRefs(store);

  return {
    documentoAbierto,
    documentoError,
    documentoUrl,
    formatoAdaptando,
    guia,
    tardaMucho,
    temaAbierto,
    temaElegido,

    adaptar: store.adaptar,
    alternarDocumento: store.alternarDocumento,
    alternarTema: store.alternarTema,
    cargarGuia: store.cargarGuia,
    elegirTema: store.elegirTema,
  };
}

export default useCmpGuia;
