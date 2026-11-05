import {
  CodigoClaseInvalidoError,
  type AutenticacionPort,
} from "@/core/autenticacion/infraestructure/ports/in/autenticacion.port";
import type { Carrera, SesionIniciada, Student } from "@/core/shared/domain/view/student.view";
import { api, esErrorApi, guardarToken } from "@/core/shared/infraestructure/http/api.client";
import type { PersonaDto, SesionDto } from "@/core/shared/infraestructure/http/api.dto";
import { CARRERAS } from "@/constants/carreras.constant";

const carreraDesdeApi = (nombre: string): string =>
  CARRERAS.find((carrera) => carrera.nombre === nombre)?.id ?? "otra";

const carreraHaciaApi = (id: string): string => CARRERAS.find((carrera) => carrera.id === id)?.nombre ?? id;

export const estudianteDesdeApi = (persona: PersonaDto): Student => ({
  alias: persona.alias,
  carrera: carreraDesdeApi(persona.career),
  rol: persona.role === "teacher" ? "docente" : "estudiante",
});

// POST /sessions, DELETE /sessions/current y PATCH /me.
export class AutenticacionUseCase implements AutenticacionPort {
  // La API no tiene catálogo de carreras: es una lista fija del front.
  obtenerCarreras(): Promise<Carrera[]> {
    return Promise.resolve(CARRERAS);
  }

  async entrar(datos: Student, codigoClase?: string): Promise<SesionIniciada> {
    try {
      const sesion = await api.post<SesionDto>("/sessions", {
        alias: datos.alias.trim(),
        career: carreraHaciaApi(datos.carrera),
        role: datos.rol === "docente" ? "teacher" : "learner",
        class_code: codigoClase?.trim() || null,
      });
      guardarToken(sesion.token);
      return {
        estudiante: estudianteDesdeApi(sesion.person),
        personaId: sesion.person.id,
        clase: sesion.membership
          ? { id: sesion.membership.class_id, nombre: sesion.membership.class_name }
          : null,
      };
    } catch (error) {
      if (esErrorApi(error, "Classrooms.InvalidCode")) {
        throw new CodigoClaseInvalidoError("No encontramos esa clase. Revisa el código con tu docente.");
      }
      throw error;
    }
  }

  async salir(): Promise<void> {
    try {
      await api.delete("/sessions/current");
    } finally {
      guardarToken(null);
    }
  }

  async cambiarAlias(alias: string): Promise<Student> {
    const persona = await api.patch<PersonaDto>("/me", { alias: alias.trim() });
    return estudianteDesdeApi(persona);
  }
}
