import { storeToRefs } from "pinia";
import { useCmpRecorridoStore } from "@/store/common/cmp-recorrido/cmp-recorrido.store";
import { useCmpSesionStore } from "@/store/common/cmp-sesion/cmp-sesion.store";

function useCmpRecorrido() {
  const store = useCmpRecorridoStore();
  const sesion = useCmpSesionStore();
  const { activo, esPrimero, esUltimo, indice, paso, pasos } = storeToRefs(store);

  // Empieza el recorrido que corresponde al rol de la persona.
  const iniciar = () => {
    if (sesion.estudiante) store.iniciar(sesion.estudiante.rol);
  };

  const terminar = () => store.terminar(sesion.personaId);

  // La primera vez que entra cada persona, el recorrido se ofrece solo.
  const debeMostrarse = () => !!sesion.personaId && !store.yaLoVio(sesion.personaId);

  return {
    activo,
    esPrimero,
    esUltimo,
    indice,
    paso,
    pasos,

    anterior: store.anterior,
    debeMostrarse,
    iniciar,
    siguiente: store.siguiente,
    terminar,
  };
}

export default useCmpRecorrido;
