import type { Verificacion } from "@/core/shared/domain/view/pregunta.view";

export interface VerificacionPort {
  obtenerVerificacion(temaId: string): Promise<Verificacion>;
  comprobarRespuesta(preguntaId: string, opcionId: string): Promise<boolean>;
}
