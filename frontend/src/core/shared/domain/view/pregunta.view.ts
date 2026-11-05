import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";

export interface OpcionPregunta {
  id: string;
  letra: string;
  texto: string;
}

export interface Pregunta {
  id: string;
  enunciado: string;
  opciones: OpcionPregunta[];
  correcta: string;
  explicacionAcierto: string;
  explicacionError: string;
  // Formato que se sugiere repasar si la respuesta no es correcta.
  formatoSugerido: FormatoId;
}

export interface Verificacion {
  ruta: string[];
  preguntas: Pregunta[];
}
