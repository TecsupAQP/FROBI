import type { ProgresoPort } from "@/core/progreso/infraestructure/ports/in/progreso.port";
import { ProgresoUseCase } from "@/core/progreso/application/use-case/progreso.use-case";

const progresoPort: ProgresoPort = new ProgresoUseCase();

export const obtenerProgresoService = (alias: string) => progresoPort.obtenerProgreso(alias);
