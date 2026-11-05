import { storeToRefs } from "pinia";
import { useCmpGuiaStore } from "@/store/business/cmp-guia/cmp-guia.store";

function useCmpGuia() {
  const store = useCmpGuiaStore();
  const { documentoAbierto, documentoError, documentoUrl, formatoAdaptando, guia, tardaMucho, temaAbierto } =
    storeToRefs(store);

  return {
    documentoAbierto,
    documentoError,
    documentoUrl,
    formatoAdaptando,
    guia,
    tardaMucho,
    temaAbierto,

    adaptar: store.adaptar,
    alternarDocumento: store.alternarDocumento,
    alternarTema: store.alternarTema,
    cargarGuia: store.cargarGuia,
  };
}

export default useCmpGuia;
