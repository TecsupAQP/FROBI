import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { EscalonId, ResultadoIntento, TareaAyuda } from "@/core/shared/domain/view/ayuda.view";
import {
  obtenerCriteriosSinIaService,
  obtenerTareaAyudaService,
  probarIntentoService,
} from "@/core/ayuda/infraestructure/adapters/in/service/ayuda.service";

const ORDEN: EscalonId[] = ["pista-1", "pista-2", "paso-a-paso", "respuesta"];

export interface ProgresoTarea {
  // Último escalón abierto. Empieza en la pista 1: nunca en la respuesta.
  alcanzado: EscalonId;
  intento: string;
  resultado: ResultadoIntento | null;
  pasoAPasoAbierto: boolean;
  respuestaSinIa: string;
  criteriosMarcados: string[];
  resueltoSinIa: boolean;
}

const progresoNuevo = (): ProgresoTarea => ({
  alcanzado: "pista-1",
  intento: "",
  resultado: null,
  pasoAPasoAbierto: false,
  respuestaSinIa: "",
  criteriosMarcados: [],
  resueltoSinIa: false,
});

// Escalera de ayuda (Figma · 20): pista 1 → pista 2 → paso a paso → respuesta final, al último.
export const useCmpEscaleraStore = defineStore("CmpEscaleraStore", () => {
  const tarea = ref<TareaAyuda | null>(null);
  const criterios = ref<string[]>([]);
  const progresos = ref<Record<string, ProgresoTarea>>({});
  const probando = ref(false);

  const progreso = computed<ProgresoTarea>(() => {
    const id = tarea.value?.id;
    return (id && progresos.value[id]) || progresoNuevo();
  });

  // La respuesta final solo se desbloquea cuando hay un intento propio.
  const respuestaDesbloqueada = computed(() => progreso.value.resultado !== null);

  const cargar = async (tareaId: string) => {
    if (tarea.value?.id !== tareaId) {
      tarea.value = await obtenerTareaAyudaService(tareaId);
      criterios.value = await obtenerCriteriosSinIaService(tareaId);
    }
    if (!progresos.value[tareaId]) {
      progresos.value[tareaId] = { ...progresoNuevo(), alcanzado: "pista-2" };
    }
  };

  const actual = (): ProgresoTarea | undefined => (tarea.value ? progresos.value[tarea.value.id] : undefined);

  const avanzar = (hasta: EscalonId) => {
    const registro = actual();
    if (!registro) return;
    if (ORDEN.indexOf(hasta) > ORDEN.indexOf(registro.alcanzado)) registro.alcanzado = hasta;
  };

  const abrirPasoAPaso = () => {
    const registro = actual();
    if (!registro) return;
    registro.pasoAPasoAbierto = true;
    avanzar("paso-a-paso");
  };

  const escribirIntento = (texto: string) => {
    const registro = actual();
    if (registro) registro.intento = texto;
  };

  const probarIntento = async () => {
    const registro = actual();
    if (!registro || !tarea.value || !registro.intento.trim()) return;
    probando.value = true;
    try {
      registro.resultado = await probarIntentoService(tarea.value.id, registro.intento);
      avanzar("respuesta");
    } finally {
      probando.value = false;
    }
  };

  const escribirRespuestaSinIa = (texto: string) => {
    const registro = actual();
    if (registro) registro.respuestaSinIa = texto;
  };

  const alternarCriterio = (criterio: string) => {
    const registro = actual();
    if (!registro) return;
    registro.criteriosMarcados = registro.criteriosMarcados.includes(criterio)
      ? registro.criteriosMarcados.filter((item) => item !== criterio)
      : [...registro.criteriosMarcados, criterio];
  };

  // Resolver sin IA es válido y cuenta como logro.
  const marcarResueltoSinIa = () => {
    const registro = actual();
    if (registro && registro.respuestaSinIa.trim()) registro.resueltoSinIa = true;
  };

  return {
    criterios,
    probando,
    progreso,
    respuestaDesbloqueada,
    tarea,

    abrirPasoAPaso,
    alternarCriterio,
    cargar,
    escribirIntento,
    escribirRespuestaSinIa,
    marcarResueltoSinIa,
    probarIntento,
  };
});
