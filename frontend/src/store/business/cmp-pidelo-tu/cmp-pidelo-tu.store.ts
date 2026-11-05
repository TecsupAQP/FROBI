import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type {
  Autonomia,
  InstruccionMejorada,
  PromptScore,
} from "@/core/shared/domain/view/prompt-score.view";
import type { PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";
import {
  contarPiezasService,
  evaluarInstruccionService,
  mejorarInstruccionService,
  obtenerAutonomiaService,
  obtenerPlantillaService,
} from "@/core/entrenador/infraestructure/adapters/in/service/entrenador.service";

// Estados de V4 (Figma · 8): vacío con plantilla → instrucción débil con pistas → comparación.
export type FasePideloTu = "escribiendo" | "evaluando" | "debil" | "mejorando" | "comparacion";

export const useCmpPideloTuStore = defineStore("CmpPideloTuStore", () => {
  const autonomia = ref<Autonomia | null>(null);
  const plantilla = ref<PiezaInstruccion[]>([]);
  const instruccion = ref("");
  const fase = ref<FasePideloTu>("escribiendo");
  const evaluacion = ref<PromptScore | null>(null);
  const mejorada = ref<InstruccionMejorada | null>(null);

  const piezasEscritas = computed(() => contarPiezasService(instruccion.value).length);
  const puedePedir = computed(() => instruccion.value.trim().length > 0 && fase.value === "escribiendo");

  const iniciar = async () => {
    fase.value = "escribiendo";
    instruccion.value = "";
    evaluacion.value = null;
    mejorada.value = null;
    const [datosAutonomia, datosPlantilla] = await Promise.all([
      obtenerAutonomiaService(),
      obtenerPlantillaService(),
    ]);
    autonomia.value = datosAutonomia;
    plantilla.value = datosPlantilla;
  };

  const usarPlantilla = () => {
    instruccion.value = plantilla.value.map((pieza) => pieza.texto).join(" ");
  };

  const pedirALaIA = async () => {
    fase.value = "evaluando";
    const resultado = await evaluarInstruccionService(instruccion.value);
    evaluacion.value = resultado;
    autonomia.value = resultado.autonomia;
    fase.value = resultado.presentes === resultado.total ? "comparacion" : "debil";
  };

  const anadirEjemplo = () => {
    const ejemplo = evaluacion.value?.sugerencia?.ejemplo;
    if (!ejemplo) return;
    instruccion.value = `${ejemplo} ${instruccion.value}`.trim();
    fase.value = "escribiendo";
  };

  const mejorarInstruccion = async () => {
    fase.value = "mejorando";
    const resultado = await mejorarInstruccionService(instruccion.value);
    mejorada.value = resultado;
    autonomia.value = resultado.autonomia;
    fase.value = "comparacion";
  };

  const probarOtra = () => {
    instruccion.value = "";
    evaluacion.value = null;
    mejorada.value = null;
    fase.value = "escribiendo";
  };

  return {
    autonomia,
    evaluacion,
    fase,
    instruccion,
    mejorada,
    piezasEscritas,
    plantilla,
    puedePedir,

    anadirEjemplo,
    iniciar,
    mejorarInstruccion,
    pedirALaIA,
    probarOtra,
    usarPlantilla,
  };
});
