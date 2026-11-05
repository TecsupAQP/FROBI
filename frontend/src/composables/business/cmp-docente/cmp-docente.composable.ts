import { storeToRefs } from "pinia";
import { useCmpDocenteStore } from "@/store/business/cmp-docente/cmp-docente.store";

function useCmpDocente() {
  const store = useCmpDocenteStore();
  const { cargado, grupoId, panel } = storeToRefs(store);

  return {
    cargado,
    grupoId,
    panel,

    cambiarGrupo: store.cambiarGrupo,
    cargar: store.cargar,
  };
}

export default useCmpDocente;
