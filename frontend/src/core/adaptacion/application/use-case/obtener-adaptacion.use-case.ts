import type { ObtenerAdaptacionPort } from "@/core/adaptacion/infraestructure/ports/in/obtener-adaptacion.port";
import type { Adaptation, FormatoId } from "@/core/shared/domain/view/adaptation.view";
import { EstadoCargaEnum } from "@/core/shared/application/enum/estado-carga.enum";
import { escenarioSimulado, respuestaSimulada } from "@/core/shared/application/util/simulacion.util";
import { adaptacionMock } from "@/mocks/adaptacion.mock";

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class ObtenerAdaptacionUseCase implements ObtenerAdaptacionPort {
  async obtenerAdaptacion(_temaId: string, formato: FormatoId): Promise<Adaptation> {
    const conRespaldo = escenarioSimulado() === EstadoCargaEnum.ERROR_RESPALDO;
    return respuestaSimulada(adaptacionMock(formato, conRespaldo), 900);
  }
}
