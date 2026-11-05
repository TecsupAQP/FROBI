import type { AyudaPort } from "@/core/ayuda/infraestructure/ports/in/ayuda.port";
import { AyudaUseCase } from "@/core/ayuda/application/use-case/ayuda.use-case";

const ayudaPort: AyudaPort = new AyudaUseCase();

export const obtenerTareaAyudaService = (tareaId: string) => ayudaPort.obtenerTarea(tareaId);
export const probarIntentoService = (tareaId: string, intento: string) =>
  ayudaPort.probarIntento(tareaId, intento);
export const obtenerCriteriosSinIaService = (tareaId: string) => ayudaPort.obtenerCriteriosSinIa(tareaId);
