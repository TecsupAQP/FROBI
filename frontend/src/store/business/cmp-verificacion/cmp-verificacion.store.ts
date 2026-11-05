import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { Verificacion } from "@/core/shared/domain/view/pregunta.view";
import {
  comprobarRespuestaService,
  obtenerVerificacionService,
} from "@/core/verificacion/infraestructure/adapters/in/service/verificacion.service";

export const useCmpVerificacionStore = defineStore("CmpVerificacionStore", () => {
  const verificacion = ref<Verificacion | null>(null);
  const indice = ref(0);
  const elegida = ref<string | null>(null);
  // Opción marcada mientras se revisa (Figma · 13 "Evaluando la respuesta").
  const revisando = ref<string | null>(null);
  const correcta = ref(false);

  const pregunta = computed(() => verificacion.value?.preguntas[indice.value] ?? null);
  const total = computed(() => verificacion.value?.preguntas.length ?? 0);
  const acerto = computed(() => elegida.value !== null && correcta.value);
  const esUltima = computed(() => indice.value >= total.value - 1);

  const cargar = async () => {
    verificacion.value = await obtenerVerificacionService();
    indice.value = 0;
    elegida.value = null;
  };

  const responder = async (opcionId: string) => {
    if (elegida.value !== null || revisando.value !== null || !pregunta.value) return;
    revisando.value = opcionId;
    try {
      const revision = await comprobarRespuestaService(pregunta.value.id, opcionId);
      // La API devuelve la explicación y, si falla, qué formato probar.
      pregunta.value.correcta = revision.opcionCorrecta;
      if (revision.correcta) pregunta.value.explicacionAcierto = revision.explicacion;
      else pregunta.value.explicacionError = revision.explicacion;
      if (revision.formatoSugerido) pregunta.value.formatoSugerido = revision.formatoSugerido;
      correcta.value = revision.correcta;
      elegida.value = opcionId;
    } finally {
      revisando.value = null;
    }
  };

  const reintentar = () => {
    elegida.value = null;
  };

  const siguiente = () => {
    if (esUltima.value) return;
    indice.value++;
    elegida.value = null;
  };

  return {
    acerto,
    elegida,
    esUltima,
    indice,
    pregunta,
    revisando,
    total,
    verificacion,
    cargar,
    reintentar,
    responder,
    siguiente,
  };
});
