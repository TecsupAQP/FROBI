// Las 4 piezas de una instrucción. Cada una tiene un color fijo en toda la app.
export type PiezaId = "contexto" | "objetivo" | "nivel" | "formato";

export interface PiezaInstruccion {
  pieza: PiezaId;
  texto: string;
}

// 1 plantilla · 2 pistas · 3 sin ayuda
export type NivelAutonomia = 1 | 2 | 3;
