import { storeToRefs } from "pinia";
import { useCmpInicioStore } from "@/store/business/cmp-inicio/cmp-inicio.store";

function useCmpInicio() {
  const store = useCmpInicioStore();
  const {
    archivo,
    archivoElegido,
    fase,
    guia,
    guiaEjemplo,
    guias,
    guiasClase,
    nombreClase,
    propias,
    sinGuia,
    modalAbierto,
    motivoError,
    nombreArchivo,
    progreso,
    tamanoArchivoMb,
  } = storeToRefs(store);

  return {
    motivoError,
    archivo,
    archivoElegido,
    fase,
    guia,
    guiaEjemplo,
    guias,
    guiasClase,
    nombreClase,
    propias,
    sinGuia,
    modalAbierto,
    nombreArchivo,
    progreso,
    tamanoArchivoMb,

    abrirModal: store.abrirModal,
    cancelarSubida: store.cancelarSubida,
    cargarGuia: store.cargarGuia,
    cerrarModal: store.cerrarModal,
    elegirArchivo: store.elegirArchivo,
    elegirGuia: store.elegirGuia,
    usarGuia: store.usarGuia,
  };
}

export default useCmpInicio;
