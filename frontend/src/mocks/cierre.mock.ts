import type { ResumenCierre } from "@/core/shared/domain/view/cierre.view";
import { RECETA_MOCK } from "@/mocks/adaptacion.mock";

export const CIERRE_MOCK: ResumenCierre = {
  tema: "Sensor inductivo",
  receta: RECETA_MOCK,
  formatoUsado: "ejemplo-real",
  piezasLogradas: ["contexto", "objetivo", "nivel", "formato"],
  totalPiezas: 4,
  autonomia: {
    nivel: 2,
    total: 3,
    nombre: "Con pistas",
    mensaje: "Un intento más sin ayuda y pasas al nivel 3.",
  },
};
