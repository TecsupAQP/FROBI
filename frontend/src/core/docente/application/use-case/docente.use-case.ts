import type { DocentePort } from "@/core/docente/infraestructure/ports/in/docente.port";
import type { PanelDocente } from "@/core/shared/domain/view/panel-docente.view";
import { respuestaSimulada } from "@/core/shared/application/util/simulacion.util";
import { PANEL_DOCENTE_MOCK } from "@/mocks/docente.mock";

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class DocenteUseCase implements DocentePort {
  obtenerPanel(grupoId: string): Promise<PanelDocente> {
    const grupo = PANEL_DOCENTE_MOCK.grupos.find((item) => item.id === grupoId) ?? PANEL_DOCENTE_MOCK.grupo;
    return respuestaSimulada({ ...PANEL_DOCENTE_MOCK, grupo });
  }
}
