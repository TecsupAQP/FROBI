import { storeToRefs } from "pinia";
import { useCmpSesionStore } from "@/store/common/cmp-sesion/cmp-sesion.store";

function useCmpSesion() {
  const store = useCmpSesionStore();
  const { estudiante, haIniciado, esDocente, inicial } = storeToRefs(store);

  return {
    estudiante,
    esDocente,
    haIniciado,
    inicial,

    cerrarSesion: store.cerrarSesion,
    iniciarSesion: store.iniciarSesion,
  };
}

export default useCmpSesion;
