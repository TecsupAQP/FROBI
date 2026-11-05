import type { PanelDocente } from "@/core/shared/domain/view/panel-docente.view";

export interface DocentePort {
  obtenerPanel(grupoId: string): Promise<PanelDocente>;
}
