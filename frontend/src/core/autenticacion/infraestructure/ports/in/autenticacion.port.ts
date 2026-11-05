import type { Carrera, Student } from "@/core/shared/domain/view/student.view";

export interface AutenticacionPort {
  obtenerCarreras(): Promise<Carrera[]>;
  // Acceso por alias: sin correo ni contraseña.
  entrar(datos: Student): Promise<Student>;
}
