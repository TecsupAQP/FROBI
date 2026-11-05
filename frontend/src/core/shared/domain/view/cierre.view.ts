import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";
import type { PiezaId, PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";

export interface ResumenCierre {
  tema: string;
  receta: PiezaInstruccion[];
  formatoUsado: FormatoId;
  piezasLogradas: PiezaId[];
  totalPiezas: number;
  autonomia: { nivel: number; total: number; nombre: string; mensaje: string };
}
