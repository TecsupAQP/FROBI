import type { AsistentePort } from "@/core/asistente/infraestructure/ports/in/asistente.port";
import { AsistenteUseCase } from "@/core/asistente/application/use-case/asistente.use-case";

const asistentePort: AsistentePort = new AsistenteUseCase();

export const leerConversacionService = () => asistentePort.leerConversacion();
export const reiniciarConversacionService = () => asistentePort.reiniciar();
export const conectarAsistenteService = (handlers: Parameters<AsistentePort["conectar"]>[0]) =>
  asistentePort.conectar(handlers);
