import { ref } from "vue";
import { defineStore } from "pinia";

export interface AvisoTemporal {
  id: number;
  titulo: string;
  detalle?: string;
}

const DURACION_MS = 4000;

// Avisos temporales (toast), p. ej. "Receta copiada".
export const useCmpAvisosStore = defineStore("CmpAvisosStore", () => {
  const avisos = ref<AvisoTemporal[]>([]);
  let siguienteId = 1;

  const quitarAviso = (id: number) => {
    avisos.value = avisos.value.filter((aviso) => aviso.id !== id);
  };

  const mostrarAviso = (titulo: string, detalle?: string) => {
    const id = siguienteId++;
    avisos.value = [...avisos.value, { id, titulo, detalle }];
    window.setTimeout(() => quitarAviso(id), DURACION_MS);
  };

  return { avisos, mostrarAviso, quitarAviso };
});
