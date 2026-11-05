import type { TrabajoPort } from "@/core/trabajo/infraestructure/ports/in/trabajo.port";
import type { BorradorTrabajo, WorkReview } from "@/core/shared/domain/view/claim-review.view";
import { respuestaSimulada } from "@/core/shared/application/util/simulacion.util";
import { BORRADOR_MOCK, REVISION_MOCK } from "@/mocks/trabajo.mock";

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class TrabajoUseCase implements TrabajoPort {
  obtenerBorradorEjemplo(): Promise<BorradorTrabajo> {
    return respuestaSimulada(BORRADOR_MOCK, 200);
  }

  revisarTrabajo(trabajo: BorradorTrabajo): Promise<WorkReview> {
    return respuestaSimulada({ ...REVISION_MOCK, consigna: trabajo.consigna }, 1200);
  }
}
