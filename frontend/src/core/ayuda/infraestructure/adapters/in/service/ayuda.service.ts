import type { AyudaPort } from "@/core/ayuda/infraestructure/ports/in/ayuda.port";
import { AyudaUseCase } from "@/core/ayuda/application/use-case/ayuda.use-case";
import type { EscalonId } from "@/core/shared/domain/view/ayuda.view";

const ayudaPort: AyudaPort = new AyudaUseCase();

export const abrirIntentoService = (tareaId: string) => ayudaPort.abrirIntento(tareaId);
export const abrirEscalonService = (intentoId: string, escalon: EscalonId) =>
  ayudaPort.abrirEscalon(intentoId, escalon);
export const enviarIntentoService = (intentoId: string, texto: string, criterios?: string[]) =>
  ayudaPort.enviarIntento(intentoId, texto, criterios);
export const obtenerCriteriosSinIaService = (tareaId: string) => ayudaPort.obtenerCriteriosSinIa(tareaId);
