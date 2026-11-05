import { storeToRefs } from "pinia";
import { useCmpClaseStore } from "@/store/common/cmp-clase/cmp-clase.store";

function useCmpClase() {
  const store = useCmpClaseStore();
  const {
    avances,
    clase,
    contenido,
    detalle,
    errorContenido,
    estoyEnClase,
    guardando,
    materiales,
    ocupado,
    subiendo,
  } = storeToRefs(store);

  return {
    avances,
    clase,
    contenido,
    errorContenido,
    subiendo,
    guardando,
    detalle,
    estoyEnClase,
    materiales,
    ocupado,

    agregarMaterial: store.agregarMaterial,
    cargar: store.cargar,
    cargarContenido: store.cargarContenido,
    cargarDetalle: store.cargarDetalle,
    crear: store.crear,
    guardarPlan: store.guardarPlan,
    invitar: store.invitar,
    salir: store.salir,
    subirContenido: store.subirContenido,
  };
}

export default useCmpClase;
