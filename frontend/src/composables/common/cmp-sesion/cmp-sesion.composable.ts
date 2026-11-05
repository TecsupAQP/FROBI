import { storeToRefs } from "pinia";
import { useCmpSesionStore } from "@/store/common/cmp-sesion/cmp-sesion.store";

function useCmpSesion() {
  const store = useCmpSesionStore();
  const { clase, estudiante, haIniciado, esDocente, inicial } = storeToRefs(store);

  return {
    clase,
    estudiante,
    esDocente,
    haIniciado,
    inicial,

    actualizarClase: store.actualizarClase,
    cambiarAlias: store.cambiarAlias,
    cambiarRol: store.cambiarRol,
    cerrarSesion: store.cerrarSesion,
    iniciarSesion: store.iniciarSesion,
    olvidarSesion: store.olvidarSesion,
  };
}

export default useCmpSesion;
