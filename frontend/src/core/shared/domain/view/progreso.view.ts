import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";

export interface AciertoFormato {
  formato: FormatoId;
  porcentaje: number;
}

export interface Progreso {
  alias: string;
  guia: string;
  mensaje: { titulo: string; texto: string };
  temasPracticados: number;
  mejorFormato: FormatoId;
  autonomia: string;
  aciertos: AciertoFormato[];
  // Piezas completas (de 4) en cada intento de "Pídelo tú".
  intentos: number[];
}
