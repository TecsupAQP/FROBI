import { storeToRefs } from "pinia";
import { useCmpEscaleraStore } from "@/store/business/cmp-escalera/cmp-escalera.store";

function useCmpEscalera() {
  const store = useCmpEscaleraStore();
  const { criterios, error, nivelAyuda, probando, progreso, respuestaDesbloqueada, tarea } =
    storeToRefs(store);

  return {
    criterios,
    error,
    nivelAyuda,
    probando,
    progreso,
    respuestaDesbloqueada,
    tarea,

    abrirPasoAPaso: store.abrirPasoAPaso,
    abrirPistas: store.abrirPistas,
    alternarCriterio: store.alternarCriterio,
    cargar: store.cargar,
    escribirIntento: store.escribirIntento,
    escribirRespuestaSinIa: store.escribirRespuestaSinIa,
    marcarResueltoSinIa: store.marcarResueltoSinIa,
    probarIntento: store.probarIntento,
  };
}

export default useCmpEscalera;
