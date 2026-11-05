import { storeToRefs } from "pinia";
import { useCmpClaseStore } from "@/store/common/cmp-clase/cmp-clase.store";

function useCmpClase() {
  const store = useCmpClaseStore();
  const { clase, detalle, estoyEnClase, materiales, ocupado } = storeToRefs(store);

  return {
    clase,
    detalle,
    estoyEnClase,
    materiales,
    ocupado,

    cargar: store.cargar,
    cargarDetalle: store.cargarDetalle,
    cargarMateriales: store.cargarMateriales,
    crear: store.crear,
    invitar: store.invitar,
    salir: store.salir,
  };
}

export default useCmpClase;
