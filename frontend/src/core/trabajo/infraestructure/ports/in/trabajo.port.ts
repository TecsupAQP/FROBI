import type { BorradorTrabajo, WorkReview } from "@/core/shared/domain/view/claim-review.view";

export interface TrabajoPort {
  obtenerBorradorEjemplo(): Promise<BorradorTrabajo>;
  revisarTrabajo(trabajo: BorradorTrabajo): Promise<WorkReview>;
}
