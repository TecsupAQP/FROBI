import type { Clase, DetalleAlumno, NuevaClase } from "@/core/shared/domain/view/clase.view";

export interface ClasePort {
  obtenerClase(): Promise<Clase | null>;
  crearClase(datos: NuevaClase): Promise<Clase>;
  // Se invita por alias: la parte antes de la @ si se escribe un correo.
  invitar(aliasOCorreo: string): Promise<Clase>;
  obtenerDetalleAlumno(alias: string): Promise<DetalleAlumno | null>;
  salirDeClase(): Promise<void>;
}
