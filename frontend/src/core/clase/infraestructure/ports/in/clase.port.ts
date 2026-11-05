import type {
  AvanceGuia,
  AvanceGuiaClase,
  Clase,
  ClaseResumen,
  DetalleAlumno,
  MaterialClase,
  NuevaClase,
  PlanGuia,
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
  // Cada material es una guía de estudio (evaluación final) o una guía con tareas.
  subirMaterial(archivo: File, plan: PlanGuia): Promise<MaterialClase[]>;
  guardarPlan(materialId: string, plan: PlanGuia): Promise<MaterialClase[]>;
  // Avance de la persona en cada guía de su clase.
  miAvance(): Promise<AvanceGuia[]>;
  // Docente: avance de cada alumno en cada guía.
  avanceClase(): Promise<AvanceGuiaClase[]>;
}
