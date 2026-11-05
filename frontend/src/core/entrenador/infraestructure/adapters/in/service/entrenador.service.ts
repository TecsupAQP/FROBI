import type { EntrenadorPort } from "@/core/entrenador/infraestructure/ports/in/entrenador.port";
import { EntrenadorUseCase } from "@/core/entrenador/application/use-case/entrenador.use-case";

const entrenadorPort: EntrenadorPort = new EntrenadorUseCase();

export const obtenerAutonomiaService = () => entrenadorPort.obtenerAutonomia();
export const obtenerPlantillaService = () => entrenadorPort.obtenerPlantilla();
export const evaluarInstruccionService = (instruccion: string) =>
  entrenadorPort.evaluarInstruccion(instruccion);
export const mejorarInstruccionService = (instruccion: string) =>
  entrenadorPort.mejorarInstruccion(instruccion);
export const contarPiezasService = (instruccion: string) => entrenadorPort.contarPiezas(instruccion);
