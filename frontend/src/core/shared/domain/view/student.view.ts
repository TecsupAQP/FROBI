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
