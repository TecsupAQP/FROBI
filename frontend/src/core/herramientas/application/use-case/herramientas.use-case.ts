import type { HerramientasPort } from "@/core/herramientas/infraestructure/ports/in/herramientas.port";
import type { RecomendacionHerramientas } from "@/core/shared/domain/view/tool.view";
import { respuestaSimulada } from "@/core/shared/application/util/simulacion.util";
import { HERRAMIENTAS_MOCK } from "@/mocks/herramientas.mock";

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class HerramientasUseCase implements HerramientasPort {
  obtenerRecomendacion(_afirmacionId: string): Promise<RecomendacionHerramientas> {
    return respuestaSimulada(HERRAMIENTAS_MOCK);
  }
}
