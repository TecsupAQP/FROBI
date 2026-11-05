import type { CierrePort } from "@/core/cierre/infraestructure/ports/in/cierre.port";
import { CierreUseCase } from "@/core/cierre/application/use-case/cierre.use-case";

const cierrePort: CierrePort = new CierreUseCase();

export const obtenerResumenCierreService = (temaId: string) => cierrePort.obtenerResumen(temaId);
