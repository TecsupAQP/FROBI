import { storeToRefs } from "pinia";
import { useCmpVerificacionStore } from "@/store/business/cmp-verificacion/cmp-verificacion.store";

function useCmpVerificacion() {
  const store = useCmpVerificacionStore();
  const { acerto, elegida, esUltima, indice, pregunta, revisando, total, verificacion } = storeToRefs(store);

  return {
    acerto,
    elegida,
    esUltima,
    indice,
    pregunta,
    revisando,
    total,
    verificacion,

    cargar: store.cargar,
    reintentar: store.reintentar,
    responder: store.responder,
    siguiente: store.siguiente,
  };
}

export default useCmpVerificacion;
