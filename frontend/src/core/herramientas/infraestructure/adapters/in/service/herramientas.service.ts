import type {
  AfirmacionRevisada,
  HerramientasPort,
} from "@/core/herramientas/infraestructure/ports/in/herramientas.port";
import { HerramientasUseCase } from "@/core/herramientas/application/use-case/herramientas.use-case";

const herramientasPort: HerramientasPort = new HerramientasUseCase();

export const obtenerRecomendacionService = (afirmacion: AfirmacionRevisada | null) =>
  herramientasPort.obtenerRecomendacion(afirmacion);
