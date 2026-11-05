// Escalera de ayuda (Figma · 20): la IA enseña el camino, nunca da la respuesta de entrada.
export type EscalonId = "pista-1" | "pista-2" | "paso-a-paso" | "respuesta";

export interface Escalon {
  id: EscalonId;
  titulo: string;
  contenido: string[];
}

export interface TareaAyuda {
  id: string;
  ruta: string[];
  titulo: string;
  enunciado: string;
  escalones: Escalon[];
}

export interface ResultadoIntento {
  correcto: boolean;
  comentario: string;
  // Fragmentos de la guía que coinciden con lo que escribió la persona.
  pasajes: string[];
}

// Estado del intento en la API: hasta qué escalón llegó y si ya puede ver la respuesta.
export interface EstadoAyuda {
  alcanzado: EscalonId | null;
  respuestaDesbloqueada: boolean;
  // "Nivel 2, con pistas"
  nivel: string;
  resueltoSinIa: boolean;
}

// Cómo se muestra cada escalón en la escalera.
export type EstadoEscalon = "hecho" | "activo" | "abierto" | "bloqueado";
