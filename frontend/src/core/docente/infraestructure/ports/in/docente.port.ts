import type { PanelDocente } from "@/core/shared/domain/view/panel-docente.view";

export interface DocentePort {
  // null si el docente todavía no creó una clase.
  obtenerPanel(): Promise<PanelDocente | null>;
}
