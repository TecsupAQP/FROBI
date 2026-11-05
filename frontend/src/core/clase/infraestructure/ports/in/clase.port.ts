import type { Clase, DetalleAlumno, NuevaClase } from "@/core/shared/domain/view/clase.view";

export interface ClasePort {
  obtenerClase(): Promise<Clase | null>;
  obtenerMateriales(): Promise<string[]>;
  crearClase(datos: NuevaClase): Promise<Clase>;
  invitarPorCorreo(correo: string): Promise<Clase>;
  obtenerDetalleAlumno(alias: string): Promise<DetalleAlumno | null>;
  salirDeClase(): Promise<void>;
}
