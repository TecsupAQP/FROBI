import type { ProgresoPort } from "@/core/progreso/infraestructure/ports/in/progreso.port";
import type { Progreso } from "@/core/shared/domain/view/progreso.view";
import { EstadoCargaEnum } from "@/core/shared/application/enum/estado-carga.enum";
import { escenarioSimulado, respuestaSimulada } from "@/core/shared/application/util/simulacion.util";
import { PROGRESO_MOCK } from "@/mocks/progreso.mock";

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class ProgresoUseCase implements ProgresoPort {
  obtenerProgreso(alias: string): Promise<Progreso | null> {
    if (escenarioSimulado() === EstadoCargaEnum.VACIO) return respuestaSimulada(null);
    return respuestaSimulada({ ...PROGRESO_MOCK, alias });
  }
}
