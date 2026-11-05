import { storeToRefs } from "pinia";
import { useCmpClaseStore } from "@/store/common/cmp-clase/cmp-clase.store";

function useCmpClase() {
  const store = useCmpClaseStore();
  const { clase, contenido, detalle, errorContenido, estoyEnClase, materiales, ocupado, subiendo } =
    storeToRefs(store);

  return {
    clase,
    contenido,
    errorContenido,
    subiendo,
    detalle,
    estoyEnClase,
    materiales,
    ocupado,

    agregarMaterial: store.agregarMaterial,
    cargar: store.cargar,
    cargarContenido: store.cargarContenido,
    cargarDetalle: store.cargarDetalle,
    crear: store.crear,
    invitar: store.invitar,
    salir: store.salir,
    subirContenido: store.subirContenido,
  };
}

export default useCmpClase;
