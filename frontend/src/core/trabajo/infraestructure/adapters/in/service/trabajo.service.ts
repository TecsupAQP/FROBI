import type { TrabajoPort } from "@/core/trabajo/infraestructure/ports/in/trabajo.port";
import { TrabajoUseCase } from "@/core/trabajo/application/use-case/trabajo.use-case";
import type { BorradorTrabajo } from "@/core/shared/domain/view/claim-review.view";

const trabajoPort: TrabajoPort = new TrabajoUseCase();

export const revisarTrabajoService = (trabajo: BorradorTrabajo) => trabajoPort.revisarTrabajo(trabajo);
