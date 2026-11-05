import type { CierrePort } from "@/core/cierre/infraestructure/ports/in/cierre.port";
import type { ResumenCierre } from "@/core/shared/domain/view/cierre.view";
import { respuestaSimulada } from "@/core/shared/application/util/simulacion.util";
import { CIERRE_MOCK } from "@/mocks/cierre.mock";

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class CierreUseCase implements CierrePort {
  obtenerResumen(_temaId: string): Promise<ResumenCierre> {
    return respuestaSimulada(CIERRE_MOCK);
  }
}
