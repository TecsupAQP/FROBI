import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { Rol } from "@/core/shared/domain/view/student.view";
import { RECORRIDO_DOCENTE, RECORRIDO_ESTUDIANTE, type PasoRecorrido } from "@/constants/recorrido.constant";

const CLAVE_VISTO = "frobi-recorrido-visto";

const leerVistos = (): string[] => {
  try {
    return JSON.parse(localStorage.getItem(CLAVE_VISTO) ?? "[]") as string[];
  } catch {
    return [];
  }
};

// Recorrido guiado por la app real: un paso por pantalla, para estudiante o docente.
export const useCmpRecorridoStore = defineStore("CmpRecorridoStore", () => {
  const activo = ref(false);
  const indice = ref(0);
  const pasos = ref<PasoRecorrido[]>([]);

  const paso = computed<PasoRecorrido | null>(() =>
    activo.value ? (pasos.value[indice.value] ?? null) : null,
  );
  const esPrimero = computed(() => indice.value === 0);
  const esUltimo = computed(() => indice.value >= pasos.value.length - 1);

  // Se recuerda por persona (personaId) para mostrarlo solo la primera vez.
  const yaLoVio = (personaId: string) => leerVistos().includes(personaId);

  const marcarVisto = (personaId: string | null) => {
    if (!personaId) return;
    try {
      const vistos = leerVistos();
      if (!vistos.includes(personaId))
        localStorage.setItem(CLAVE_VISTO, JSON.stringify([...vistos, personaId]));
    } catch {
      // Sin almacenamiento: se volverá a ofrecer en la próxima visita.
    }
  };

  const iniciar = (rol: Rol) => {
    pasos.value = rol === "docente" ? RECORRIDO_DOCENTE : RECORRIDO_ESTUDIANTE;
    indice.value = 0;
    activo.value = true;
  };

  const siguiente = () => {
    if (!esUltimo.value) indice.value++;
  };

  const anterior = () => {
    if (!esPrimero.value) indice.value--;
  };

  const terminar = (personaId: string | null) => {
    activo.value = false;
    marcarVisto(personaId);
  };

  return {
    activo,
    esPrimero,
    esUltimo,
    indice,
    paso,
    pasos,
    anterior,
    iniciar,
    siguiente,
    terminar,
    yaLoVio,
  };
});
