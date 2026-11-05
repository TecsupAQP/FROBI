import type { ObtenerAdaptacionPort } from "@/core/adaptacion/infraestructure/ports/in/obtener-adaptacion.port";
import { ObtenerAdaptacionUseCase } from "@/core/adaptacion/application/use-case/obtener-adaptacion.use-case";
import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";

const obtenerAdaptacionPort: ObtenerAdaptacionPort = new ObtenerAdaptacionUseCase();

export const obtenerAdaptacionService = (temaId: string, formato: FormatoId) =>
  obtenerAdaptacionPort.obtenerAdaptacion(temaId, formato);
