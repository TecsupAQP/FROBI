import type { Escalon } from "@/core/shared/domain/view/ayuda.view";

// Los 4 escalones de la escalera de ayuda (RF39). Su contenido lo entrega la API al abrir cada uno.
export const ESCALONES_AYUDA: Escalon[] = [
  { id: "pista-1", titulo: "Pista 1", contenido: [] },
  { id: "pista-2", titulo: "Pista 2", contenido: [] },
  { id: "paso-a-paso", titulo: "Paso a paso", contenido: [] },
  { id: "respuesta", titulo: "Respuesta final", contenido: [] },
];

// Autoevaluación de "Inténtalo sin IA": sirve para cualquier tema.
export const CRITERIOS_SIN_IA = ["Lo expliqué con mis palabras", "Di un ejemplo o un caso", "Revisé mi guía"];
