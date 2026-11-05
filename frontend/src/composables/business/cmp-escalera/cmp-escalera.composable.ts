import { storeToRefs } from "pinia";
import { useCmpEscaleraStore } from "@/store/business/cmp-escalera/cmp-escalera.store";

function useCmpEscalera() {
  const store = useCmpEscaleraStore();
  const {
    abriendo,
    criterios,
    error,
    nivelAyuda,
    probando,
    progreso,
    respuestaDesbloqueada,
    siguiente,
    tarea,
  } = storeToRefs(store);

  return {
    abriendo,
    criterios,
    error,
    nivelAyuda,
    probando,
    progreso,
    respuestaDesbloqueada,
    siguiente,
    tarea,

    abrirSiguiente: store.abrirSiguiente,
    alternarCriterio: store.alternarCriterio,
    cargar: store.cargar,
    escribirIntento: store.escribirIntento,
    escribirRespuestaSinIa: store.escribirRespuestaSinIa,
    marcarResueltoSinIa: store.marcarResueltoSinIa,
    probarIntento: store.probarIntento,
  };
}

export default useCmpEscalera;
