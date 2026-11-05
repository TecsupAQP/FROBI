import type { Adaptation, FormatoId } from "@/core/shared/domain/view/adaptation.view";

export interface ObtenerAdaptacionPort {
  obtenerAdaptacion(temaId: string, formato: FormatoId): Promise<Adaptation>;
}
