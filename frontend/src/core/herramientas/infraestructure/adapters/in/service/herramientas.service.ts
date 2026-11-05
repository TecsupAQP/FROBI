import type { HerramientasPort } from "@/core/herramientas/infraestructure/ports/in/herramientas.port";
import { HerramientasUseCase } from "@/core/herramientas/application/use-case/herramientas.use-case";

const herramientasPort: HerramientasPort = new HerramientasUseCase();

export const obtenerRecomendacionService = (afirmacionId: string) =>
  herramientasPort.obtenerRecomendacion(afirmacionId);
