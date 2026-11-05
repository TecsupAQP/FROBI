import type { AutenticacionPort } from "@/core/autenticacion/infraestructure/ports/in/autenticacion.port";
import type { Carrera, Student } from "@/core/shared/domain/view/student.view";
import { respuestaSimulada } from "@/core/shared/application/util/simulacion.util";
import { CARRERAS_MOCK } from "@/mocks/sesion.mock";

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class AutenticacionUseCase implements AutenticacionPort {
  obtenerCarreras(): Promise<Carrera[]> {
    return respuestaSimulada(CARRERAS_MOCK, 150);
  }

  entrar(datos: Student): Promise<Student> {
    return respuestaSimulada({ ...datos, alias: datos.alias.trim() }, 400);
  }
}
