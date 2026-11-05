import type { ClasePort } from "@/core/clase/infraestructure/ports/in/clase.port";
import type { Clase, DetalleAlumno, NuevaClase } from "@/core/shared/domain/view/clase.view";
import { respuestaSimulada } from "@/core/shared/application/util/simulacion.util";
import { CLASE_MOCK, DETALLES_ALUMNO_MOCK, MATERIALES_CLASE_MOCK } from "@/mocks/clase.mock";

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class ClaseUseCase implements ClasePort {
  private clase: Clase = structuredClone(CLASE_MOCK);

  obtenerClase(): Promise<Clase | null> {
    return respuestaSimulada(this.clase, 400);
  }

  obtenerMateriales(): Promise<string[]> {
    return respuestaSimulada(MATERIALES_CLASE_MOCK, 300);
  }

  crearClase(datos: NuevaClase): Promise<Clase> {
    this.clase = { ...this.clase, nombre: datos.nombre, carrera: datos.carrera, ciclo: datos.ciclo };
    return respuestaSimulada(this.clase, 700);
  }

  invitarPorCorreo(correo: string): Promise<Clase> {
    const alias = correo.split("@")[0] ?? correo;
    if (!this.clase.alumnos.some((alumno) => alumno.alias === alias)) {
      this.clase.alumnos.push({
        alias,
        nombre: correo,
        estado: "invitado",
        avance: 0,
        posicion: "Todavía no empieza",
        nota: "Invitación enviada por correo.",
        alerta: null,
      });
    }
    return respuestaSimulada(this.clase, 600);
  }

  obtenerDetalleAlumno(alias: string): Promise<DetalleAlumno | null> {
    return respuestaSimulada(DETALLES_ALUMNO_MOCK[alias] ?? null, 500);
  }

  salirDeClase(): Promise<void> {
    return respuestaSimulada(undefined, 400);
  }
}
