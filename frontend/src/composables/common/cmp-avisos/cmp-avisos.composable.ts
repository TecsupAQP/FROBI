import { storeToRefs } from "pinia";
import { useCmpAvisosStore } from "@/store/common/cmp-avisos/cmp-avisos.store";

function useCmpAvisos() {
  const store = useCmpAvisosStore();
  const { avisos } = storeToRefs(store);

  return {
    avisos,

    mostrarAviso: store.mostrarAviso,
    quitarAviso: store.quitarAviso,
  };
}

export default useCmpAvisos;
