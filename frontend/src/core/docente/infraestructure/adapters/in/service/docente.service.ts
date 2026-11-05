import type { DocentePort } from "@/core/docente/infraestructure/ports/in/docente.port";
import { DocenteUseCase } from "@/core/docente/application/use-case/docente.use-case";

const docentePort: DocentePort = new DocenteUseCase();

export const obtenerPanelDocenteService = (grupoId: string) => docentePort.obtenerPanel(grupoId);
