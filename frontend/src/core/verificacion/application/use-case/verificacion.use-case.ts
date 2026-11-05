import type { VerificacionPort } from "@/core/verificacion/infraestructure/ports/in/verificacion.port";
import type { Verificacion } from "@/core/shared/domain/view/pregunta.view";
import { respuestaSimulada } from "@/core/shared/application/util/simulacion.util";
import { VERIFICACION_MOCK } from "@/mocks/verificacion.mock";

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class VerificacionUseCase implements VerificacionPort {
  obtenerVerificacion(_temaId: string): Promise<Verificacion> {
    return respuestaSimulada(VERIFICACION_MOCK);
  }

  comprobarRespuesta(preguntaId: string, opcionId: string): Promise<boolean> {
    const pregunta = VERIFICACION_MOCK.preguntas.find((item) => item.id === preguntaId);
    return respuestaSimulada(pregunta?.correcta === opcionId, 800);
  }
}
