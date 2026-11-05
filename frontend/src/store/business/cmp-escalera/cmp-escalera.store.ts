import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type {
  EscalonId,
  EstadoAyuda,
  ResultadoIntento,
  TareaAyuda,
} from "@/core/shared/domain/view/ayuda.view";
import {
  abrirEscalonService,
  abrirIntentoService,
  enviarIntentoService,
  obtenerCriteriosSinIaService,
} from "@/core/ayuda/infraestructure/adapters/in/service/ayuda.service";

const ORDEN: EscalonId[] = ["pista-1", "pista-2", "paso-a-paso", "respuesta"];

export interface ProgresoTarea {
  // Último escalón abierto; null mientras no se pida ninguna ayuda.
  alcanzado: EscalonId | null;
  intento: string;
  resultado: ResultadoIntento | null;
  pasoAPasoAbierto: boolean;
  respuestaSinIa: string;
  criteriosMarcados: string[];
  resueltoSinIa: boolean;
  // Fragmentos de la guía con los que se compara la respuesta sin IA.
  pasajesGuia: string[];
}

const progresoNuevo = (): ProgresoTarea => ({
  alcanzado: null,
  intento: "",
  resultado: null,
  pasoAPasoAbierto: false,
  respuestaSinIa: "",
  criteriosMarcados: [],
  resueltoSinIa: false,
  pasajesGuia: [],
});

// Escalera de ayuda (Figma · 20): pista 1 → pista 2 → paso a paso → respuesta final, al último.
// La escalera y "Inténtalo sin IA" usan intentos distintos en la API: practicar sin IA
// cuenta como logro aunque antes se hayan pedido pistas.
export const useCmpEscaleraStore = defineStore("CmpEscaleraStore", () => {
  const tarea = ref<TareaAyuda | null>(null);
  const criterios = ref<string[]>([]);
  const progresos = ref<Record<string, ProgresoTarea>>({});
  const intentos = ref<Record<string, { escalera?: string; sinIa?: string }>>({});
  const estado = ref<EstadoAyuda | null>(null);
  const probando = ref(false);
  const error = ref<string | null>(null);

  const progreso = computed<ProgresoTarea>(() => {
    const id = tarea.value?.id;
    return (id && progresos.value[id]) || progresoNuevo();
  });

  // La respuesta final solo se desbloquea cuando hay un intento propio.
  const respuestaDesbloqueada = computed(() => estado.value?.respuestaDesbloqueada ?? false);

  // El siguiente escalón que se puede pedir (RF39: cada uno se abre solo si la persona lo pide).
  const siguiente = computed<EscalonId | null>(() => {
    const alcanzado = progreso.value.alcanzado;
    const proximo = ORDEN[alcanzado ? ORDEN.indexOf(alcanzado) + 1 : 0] ?? null;
    if (proximo === "respuesta" && !respuestaDesbloqueada.value) return null;
    return proximo;
  });

  const nivelAyuda = computed(() => estado.value?.nivel ?? "Nivel 0, sin ayuda");

  const actual = (): ProgresoTarea | undefined => (tarea.value ? progresos.value[tarea.value.id] : undefined);

  const ponerContenido = (id: EscalonId, contenido: string[]) => {
    const escalon = tarea.value?.escalones.find((item) => item.id === id);
    if (escalon) escalon.contenido = contenido;
  };

  const avanzar = (hasta: EscalonId) => {
    const registro = actual();
    if (!registro) return;
    const actualIndice = registro.alcanzado ? ORDEN.indexOf(registro.alcanzado) : -1;
    if (ORDEN.indexOf(hasta) > actualIndice) registro.alcanzado = hasta;
    if (hasta === "paso-a-paso") registro.pasoAPasoAbierto = true;
  };

  const abrir = async (id: EscalonId) => {
    const intentoId = tarea.value && intentos.value[tarea.value.id]?.escalera;
    if (!intentoId) return;
    const abierto = await abrirEscalonService(intentoId, id);
    ponerContenido(id, abierto.contenido);
    estado.value = abierto.estado;
    avanzar(id);
  };

  const cargar = async (tareaId: string) => {
    error.value = null;
    if (tarea.value?.id === tareaId) return;
    try {
      criterios.value = await obtenerCriteriosSinIaService(tareaId);
      const abierto = await abrirIntentoService(tareaId);
      tarea.value = abierto?.tarea ?? null;
      if (!abierto) {
        error.value = "No encontramos ese tema en tu guía. Elige uno desde la guía.";
        return;
      }
      intentos.value[tareaId] = { escalera: abierto.intentoId };
      estado.value = abierto.estado;
      progresos.value[tareaId] = progresoNuevo();
    } catch {
      error.value = "No pudimos preparar las pistas. Revisa tu conexión e inténtalo de nuevo.";
    }
  };

  const abriendo = ref(false);

  const abrirSiguiente = async () => {
    const proximo = siguiente.value;
    if (!proximo || abriendo.value) return;
    abriendo.value = true;
    error.value = null;
    try {
      await abrir(proximo);
    } catch {
      error.value = "No pudimos abrir esta ayuda. Inténtalo de nuevo.";
    } finally {
      abriendo.value = false;
    }
  };

  const escribirIntento = (texto: string) => {
    const registro = actual();
    if (registro) registro.intento = texto;
  };

  const probarIntento = async () => {
    const registro = actual();
    const intentoId = tarea.value && intentos.value[tarea.value.id]?.escalera;
    if (!registro || !intentoId || !registro.intento.trim()) return;
    probando.value = true;
    try {
      const revision = await enviarIntentoService(intentoId, registro.intento);
      estado.value = revision.estado;
      registro.resultado = revision.resultado;
    } catch {
      error.value = "No pudimos revisar tu intento. Inténtalo de nuevo.";
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

  // Resolver sin IA es válido y cuenta como logro. Devuelve si la API lo registró como tal.
  const marcarResueltoSinIa = async (): Promise<boolean> => {
    const registro = actual();
    if (!tarea.value || !registro || !registro.respuestaSinIa.trim()) return false;
    probando.value = true;
    try {
      const propios = intentos.value[tarea.value.id] ?? {};
      if (!propios.sinIa) {
        const abierto = await abrirIntentoService(tarea.value.id);
        if (!abierto) return false;
        propios.sinIa = abierto.intentoId;
        intentos.value[tarea.value.id] = propios;
      }
      const revision = await enviarIntentoService(
        propios.sinIa,
        registro.respuestaSinIa,
        registro.criteriosMarcados,
      );
      registro.pasajesGuia = revision.resultado.pasajes;
      registro.resueltoSinIa = revision.estado.resueltoSinIa;
      return registro.resueltoSinIa;
    } catch {
      error.value = "No pudimos comparar tu respuesta. Inténtalo de nuevo.";
      return false;
    } finally {
      probando.value = false;
    }
  };

  // Al cambiar de guía, los intentos abiertos quedan atados a la adaptación anterior.
  const reiniciar = () => {
    tarea.value = null;
    progresos.value = {};
    intentos.value = {};
    estado.value = null;
    error.value = null;
  };

  return {
    criterios,
    error,
    nivelAyuda,
    probando,
    progreso,
    respuestaDesbloqueada,
    tarea,

    abriendo,
    siguiente,

    abrirSiguiente,
    alternarCriterio,
    cargar,
    escribirIntento,
    escribirRespuestaSinIa,
    marcarResueltoSinIa,
    probarIntento,
    reiniciar,
  };
});
