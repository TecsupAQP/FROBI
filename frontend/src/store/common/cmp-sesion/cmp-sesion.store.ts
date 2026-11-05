import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { Student } from "@/core/shared/domain/view/student.view";

const CLAVE_ALMACEN = "frobi-sesion";

const leerSesionGuardada = (): Student | null => {
  try {
    const guardada = sessionStorage.getItem(CLAVE_ALMACEN);
    return guardada ? (JSON.parse(guardada) as Student) : null;
  } catch {
    return null;
  }
};

// Sesión simulada: no hay autenticación real, solo alias/carrera/rol en memoria.
export const useCmpSesionStore = defineStore("CmpSesionStore", () => {
  const estudiante = ref<Student | null>(leerSesionGuardada());

  const haIniciado = computed(() => estudiante.value !== null);
  const esDocente = computed(() => estudiante.value?.rol === "docente");
  const inicial = computed(() => estudiante.value?.alias.charAt(0).toUpperCase() ?? "");

  const iniciarSesion = (datos: Student) => {
    estudiante.value = datos;
    try {
      sessionStorage.setItem(CLAVE_ALMACEN, JSON.stringify(datos));
    } catch {
      // Sin almacenamiento disponible: la sesión vive solo en memoria.
    }
  };

  const cerrarSesion = () => {
    estudiante.value = null;
    try {
      sessionStorage.removeItem(CLAVE_ALMACEN);
    } catch {
      // Nada que limpiar.
    }
  };

  return { estudiante, haIniciado, esDocente, inicial, iniciarSesion, cerrarSesion };
});
