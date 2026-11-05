import type { VerificacionPort } from "@/core/verificacion/infraestructure/ports/in/verificacion.port";
import { VerificacionUseCase } from "@/core/verificacion/application/use-case/verificacion.use-case";

const verificacionPort: VerificacionPort = new VerificacionUseCase();

export const obtenerVerificacionService = (temaId: string) => verificacionPort.obtenerVerificacion(temaId);
export const comprobarRespuestaService = (preguntaId: string, opcionId: string) =>
  verificacionPort.comprobarRespuesta(preguntaId, opcionId);
