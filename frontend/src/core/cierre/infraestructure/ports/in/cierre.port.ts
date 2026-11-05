import type { ResumenCierre } from "@/core/shared/domain/view/cierre.view";

export interface CierrePort {
  obtenerResumen(temaId: string): Promise<ResumenCierre>;
}
