import type { AutenticacionPort } from "@/core/autenticacion/infraestructure/ports/in/autenticacion.port";
import { AutenticacionUseCase } from "@/core/autenticacion/application/use-case/autenticacion.use-case";
import type { Student } from "@/core/shared/domain/view/student.view";

const autenticacionPort: AutenticacionPort = new AutenticacionUseCase();

export const obtenerCarrerasService = () => autenticacionPort.obtenerCarreras();
export const entrarService = (datos: Student) => autenticacionPort.entrar(datos);
