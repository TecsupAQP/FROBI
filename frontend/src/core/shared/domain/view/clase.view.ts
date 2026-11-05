// Puerta de clase: el docente crea una clase, invita con un código y ve avances dentro de ella.
export type EstadoAlumno = "invitado" | "se-unio" | "salio";

export type TipoAlerta = "va-bien" | "se-traba";

export interface AlertaAlumno {
  tipo: TipoAlerta;
  texto: string;
}

export interface AlumnoClase {
  // null mientras la invitación esté pendiente (aún no entró a FROBI).
  personaId: string | null;
  alias: string;
  nombre: string;
  estado: EstadoAlumno;
  // Avance de la tarea actual, en porcentaje. null si la API todavía no lo informa.
  avance: number | null;
  // Dónde va en la escalera: "Pista 2 de 4 · tarea 1 de 3".
  posicion: string;
  nota: string;
  alerta: AlertaAlumno | null;
}

export interface Clase {
  id: string;
  nombre: string;
  carrera: string;
  ciclo: string;
  codigo: string;
  alumnos: AlumnoClase[];
  // true mientras el panel muestre datos de ejemplo (sample_data en la API).
  esEjemplo: boolean;
}

// Una clase en la lista "Mis clases" del docente.
export interface ClaseResumen {
  id: string;
  nombre: string;
  codigo: string;
}

// Material que el docente sube a la clase: lo ven sus alumnos unidos.
// Guía de estudio: sin tareas, la IA evalúa al final. Guía con tareas: las escribe el docente.
export type ModoGuia = "estudio" | "tareas";

export interface TareaGuia {
  id: string;
  numero: number;
  enunciado: string;
  // Lo que la escalera de ayuda registra como tarea ("tarea-{id}").
  ref: string;
}

export interface MaterialClase {
  id: string;
  titulo: string;
  vistaPrevia: string;
  fecha: string;
  modo: ModoGuia;
  tareas: TareaGuia[];
}

export interface PlanGuia {
  modo: ModoGuia;
  tareas: string[];
}

// Avance de 0 a 100: tareas hechas sobre el total, o aciertos de la evaluación final.
export interface AvanceGuia {
  materialId: string;
  modo: ModoGuia;
  avance: number;
  tareasHechas: string[];
  evaluacion: { aciertos: number; total: number } | null;
}

export interface AvanceGuiaClase {
  materialId: string;
  titulo: string;
  modo: ModoGuia;
  totalTareas: number;
  alumnos: { personaId: string; alias: string; avance: number }[];
}

export interface NuevaClase {
  nombre: string;
  carrera: string;
  ciclo: string;
  tareas: string[];
  // PDFs que se suben a la clase apenas existe.
  archivos: File[];
}

export interface UsoEscalon {
  texto: string;
  usado: boolean;
}

export interface MensajeConversacion {
  autor: "alumno" | "frobi";
  etiqueta: string;
  texto: string;
}

export interface DetalleAlumno {
  alumno: AlumnoClase;
  clase: string;
  ultimoAcceso?: string;
  usoEscalera: UsoEscalon[];
  resueltosSinIa: { hechos: number; total: number };
  competencias: { etiqueta: string; porcentaje: number }[];
  conversacion: MensajeConversacion[];
  sugerencia: string;
  esEjemplo: boolean;
}
