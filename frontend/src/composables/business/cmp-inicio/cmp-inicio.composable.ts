import { storeToRefs } from "pinia";
import { useCmpInicioStore } from "@/store/business/cmp-inicio/cmp-inicio.store";

function useCmpInicio() {
  const store = useCmpInicioStore();
  const { archivo, fase, guia, modalAbierto, nombreArchivo, progreso, tamanoArchivoMb } = storeToRefs(store);

  return {
    archivo,
    fase,
    guia,
    modalAbierto,
    nombreArchivo,
    progreso,
    tamanoArchivoMb,

    abrirModal: store.abrirModal,
    cancelarSubida: store.cancelarSubida,
    cargarGuia: store.cargarGuia,
    cerrarModal: store.cerrarModal,
    elegirArchivo: store.elegirArchivo,
  };
}

export default useCmpInicio;
