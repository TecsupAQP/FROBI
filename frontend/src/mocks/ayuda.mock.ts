import type { TareaAyuda } from "@/core/shared/domain/view/ayuda.view";

export const TAREAS_AYUDA_MOCK: Record<string, TareaAyuda> = {
  "sensor-vidrio": {
    id: "sensor-vidrio",
    ruta: ["Tarea 1 de 3", "Sensores industriales"],
    titulo: "¿Qué sensor detecta botellas de vidrio?",
    enunciado: "¿Qué sensor usarías para detectar botellas de vidrio en una faja? Explica por qué.",
    escalones: [
      {
        id: "pista-1",
        titulo: "Pista 1",
        contenido: ["Revisa en tu guía qué material detecta cada sensor."],
      },
      {
        id: "pista-2",
        titulo: "Pista 2",
        contenido: ["Compara el sensor inductivo y el capacitivo: ¿cuál detecta vidrio?"],
      },
      {
        id: "paso-a-paso",
        titulo: "Paso a paso",
        contenido: [
          "1. La botella es de vidrio, no de metal.",
          "2. El inductivo solo detecta metales.",
          "3. El capacitivo detecta metales, plásticos, líquidos y vidrio.",
        ],
      },
      {
        id: "respuesta",
        titulo: "Respuesta final",
        contenido: [
          "El sensor capacitivo, porque detecta materiales que no son metal, como el vidrio. El inductivo solo vería la tapa metálica.",
        ],
      },
    ],
  },
};

export const CRITERIOS_SIN_IA_MOCK = [
  "Nombré el sensor",
  "Expliqué por qué sirve para vidrio",
  "Revisé mi guía",
];
