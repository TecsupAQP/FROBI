import type {
  Autonomia,
  InstruccionMejorada,
  PromptScore,
} from "@/core/shared/domain/view/prompt-score.view";
import type { PiezaId, PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";

export interface EntrenadorPort {
  obtenerAutonomia(): Promise<Autonomia>;
  obtenerPlantilla(): Promise<PiezaInstruccion[]>;
  evaluarInstruccion(instruccion: string): Promise<PromptScore>;
  mejorarInstruccion(instruccion: string): Promise<InstruccionMejorada>;
  // Conteo rápido mientras se escribe (sin llamar a la IA).
  contarPiezas(instruccion: string): PiezaId[];
}
