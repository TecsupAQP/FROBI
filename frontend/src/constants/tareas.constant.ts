import type { TareaAyuda } from "@/core/shared/domain/view/ayuda.view";

// Tareas de práctica. La API recibe solo su referencia (task_ref) y entrega el contenido
// de cada escalón cuando se abre.
export const TAREAS: Record<string, TareaAyuda> = {
  "sensor-vidrio": {
    id: "sensor-vidrio",
    ruta: ["Tarea 1 de 3", "Sensores industriales"],
    titulo: "¿Qué sensor detecta botellas de vidrio?",
    enunciado: "¿Qué sensor usarías para detectar botellas de vidrio en una faja? Explica por qué.",
    escalones: [
      { id: "pista-1", titulo: "Pista 1", contenido: [] },
      { id: "pista-2", titulo: "Pista 2", contenido: [] },
      { id: "paso-a-paso", titulo: "Paso a paso", contenido: [] },
      { id: "respuesta", titulo: "Respuesta final", contenido: [] },
    ],
  },
};

// Autoevaluación de "Inténtalo sin IA".
export const CRITERIOS_SIN_IA = ["Nombré el sensor", "Expliqué por qué sirve para vidrio", "Revisé mi guía"];
