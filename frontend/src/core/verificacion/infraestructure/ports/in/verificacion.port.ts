import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";
import type { Verificacion } from "@/core/shared/domain/view/pregunta.view";

export interface RespuestaRevisada {
  correcta: boolean;
  opcionCorrecta: string;
  explicacion: string;
  // "Prueba con…": formato para repasar cuando la respuesta no es correcta.
  formatoSugerido: FormatoId | null;
}

export interface VerificacionPort {
  // 2 o 3 preguntas sobre la adaptación que se acaba de estudiar.
  obtenerVerificacion(): Promise<Verificacion>;
  comprobarRespuesta(preguntaId: string, opcionId: string): Promise<RespuestaRevisada>;
}
