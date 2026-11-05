import type {
  Clase,
  ClaseResumen,
  DetalleAlumno,
  MaterialClase,
  NuevaClase,
} from "@/core/shared/domain/view/clase.view";

export interface ClasePort {
  // La clase elegida: la del docente (puede tener varias) o la del estudiante unido.
  obtenerClase(): Promise<Clase | null>;
  // Todas las clases del docente, la más reciente primero.
  listarClases(): Promise<ClaseResumen[]>;
  // Cambia la clase con la que trabaja el docente (panel, invitar, contenido).
  elegirClase(claseId: string): void;
  crearClase(datos: NuevaClase): Promise<Clase>;
  // Se invita por alias: la parte antes de la @ si se escribe un correo.
  invitar(aliasOCorreo: string): Promise<Clase>;
  obtenerDetalleAlumno(alias: string): Promise<DetalleAlumno | null>;
  salirDeClase(): Promise<void>;
  // Contenido de la clase: lo sube el docente y lo ven sus alumnos unidos.
  listarMateriales(): Promise<MaterialClase[]>;
  subirMaterial(archivo: File): Promise<MaterialClase[]>;
}
