import type { NivelAutonomia, PiezaId, PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";

export interface EvaluacionPieza {
  pieza: PiezaId;
  presente: boolean;
  // "Falta: ¿quién eres y qué estudias?" o "Pides una explicación."
  comentario: string;
}

export interface Sugerencia {
  texto: string;
  ejemplo: string;
}

export interface PromptScore {
  instruccion: string;
  piezas: EvaluacionPieza[];
  presentes: number;
  total: number;
  sugerencia: Sugerencia | null;
  // Tras evaluar, la persona puede subir de nivel de autonomía.
  autonomia: Autonomia;
}

export interface InstruccionMejorada {
  receta: PiezaInstruccion[];
  resultado: string[];
  autonomia: Autonomia;
}

export type EstadoNivel = "superado" | "actual" | "bloqueado";

export interface NivelAutonomiaView {
  nivel: NivelAutonomia;
  nombre: string;
  estado: EstadoNivel;
}

export interface Autonomia {
  nivelActual: NivelAutonomia;
  niveles: NivelAutonomiaView[];
  mensaje: string;
}
