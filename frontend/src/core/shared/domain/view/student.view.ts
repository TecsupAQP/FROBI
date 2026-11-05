export type Rol = "estudiante" | "docente";

export interface Student {
  alias: string;
  carrera: string;
  rol: Rol;
}

export interface Carrera {
  id: string;
  nombre: string;
}

// Sesión abierta en la API: la persona y, si entró con código, su clase.
export interface SesionIniciada {
  estudiante: Student;
  personaId: string;
  clase: { id: string; nombre: string } | null;
}
