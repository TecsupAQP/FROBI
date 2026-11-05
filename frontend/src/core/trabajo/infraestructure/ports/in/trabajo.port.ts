import type { BorradorTrabajo, WorkReview } from "@/core/shared/domain/view/claim-review.view";

export interface TrabajoPort {
  revisarTrabajo(trabajo: BorradorTrabajo): Promise<WorkReview>;
}
