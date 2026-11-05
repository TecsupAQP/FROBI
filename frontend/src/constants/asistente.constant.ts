import type { NombreIcono } from "@/constants/iconos.constant";

export interface SugerenciaAsistente {
  icono: NombreIcono;
  titulo: string;
  pregunta: string;
}

// Para empezar la conversación con un toque (Pregúntale a FROBI).
export const SUGERENCIAS_ESTUDIANTE: SugerenciaAsistente[] = [
  { icono: "gauge", titulo: "Mi rendimiento", pregunta: "¿Cómo voy y qué me conviene practicar ahora?" },
  { icono: "book", titulo: "Mi guía", pregunta: "Explícame con palabras simples la guía que tengo abierta." },
  {
    icono: "help",
    titulo: "Me trabé",
    pregunta: "Me trabé en una tarea, ¿cómo me ayudas sin darme la respuesta?",
  },
  { icono: "info", titulo: "Usar FROBI", pregunta: "¿Cómo subo mi guía y elijo un formato para estudiar?" },
];

export const SUGERENCIAS_DOCENTE: SugerenciaAsistente[] = [
  { icono: "warn", titulo: "Alertas", pregunta: "¿Quién de mi clase necesita apoyo y por qué?" },
  {
    icono: "chart",
    titulo: "Resumen de la clase",
    pregunta: "Resume el rendimiento de mi clase y qué formato funciona mejor.",
  },
  {
    icono: "search",
    titulo: "Preguntas difíciles",
    pregunta: "¿Qué preguntas fallan más mis alumnos y cómo puedo reforzarlas?",
  },
  {
    icono: "users",
    titulo: "Usar FROBI",
    pregunta: "¿Cómo invito a mis alumnos y subo el contenido de la clase?",
  },
];
