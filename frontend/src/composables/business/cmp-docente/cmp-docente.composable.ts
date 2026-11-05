import { storeToRefs } from "pinia";
import { useCmpDocenteStore } from "@/store/business/cmp-docente/cmp-docente.store";

function useCmpDocente() {
  const store = useCmpDocenteStore();
  const { grupoId, panel } = storeToRefs(store);

  return {
    grupoId,
    panel,

    cambiarGrupo: store.cambiarGrupo,
    cargar: store.cargar,
  };
}

export default useCmpDocente;
