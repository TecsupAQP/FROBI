import type { Progreso } from "@/core/shared/domain/view/progreso.view";

export const PROGRESO_MOCK: Progreso = {
  alias: "mecatronico_01",
  guia: "Sensores industriales",
  mensaje: {
    titulo: "Aprendes mejor con ejemplos reales",
    texto:
      "Aciertas el 90 % con Ejemplo real. Audio es el que más te cuesta (60 %). Prueba tu próximo tema con un ejemplo.",
  },
  temasPracticados: 3,
  mejorFormato: "ejemplo-real",
  autonomia: "Nivel 2 · Con pistas",
  aciertos: [
    { formato: "mapa-visual", porcentaje: 70 },
    { formato: "ejemplo-real", porcentaje: 90 },
    { formato: "lectura-facil", porcentaje: 75 },
    { formato: "audio", porcentaje: 60 },
  ],
  intentos: [1, 1, 2, 3, 4],
};
