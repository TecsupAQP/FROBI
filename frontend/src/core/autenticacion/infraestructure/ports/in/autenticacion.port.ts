import type { Carrera, SesionIniciada, Student } from "@/core/shared/domain/view/student.view";

export class CodigoClaseInvalidoError extends Error {
  constructor(mensaje: string) {
    super(mensaje);
    this.name = "CodigoClaseInvalidoError";
  }
}

export interface AutenticacionPort {
  obtenerCarreras(): Promise<Carrera[]>;
  // Acceso por alias: sin correo ni contraseña. El código de clase es opcional.
  entrar(datos: Student, codigoClase?: string): Promise<SesionIniciada>;
  salir(): Promise<void>;
  cambiarAlias(alias: string): Promise<Student>;
}
