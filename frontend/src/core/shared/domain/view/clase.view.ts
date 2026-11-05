// Puerta de clase: el docente crea una clase, invita con un código y ve avances dentro de ella.
export type EstadoAlumno = "invitado" | "se-unio" | "salio";

export type TipoAlerta = "va-bien" | "se-traba";

export interface AlertaAlumno {
  tipo: TipoAlerta;
  texto: string;
}

export interface AlumnoClase {
  alias: string;
  nombre: string;
  estado: EstadoAlumno;
  // Avance de la tarea actual, en porcentaje.
  avance: number;
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
  esEjemplo: true;
}

export interface NuevaClase {
  nombre: string;
  carrera: string;
  ciclo: string;
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
  ultimoAcceso: string;
  usoEscalera: UsoEscalon[];
  resueltosSinIa: { hechos: number; total: number };
  competencias: { etiqueta: string; porcentaje: number }[];
  conversacion: MensajeConversacion[];
  sugerencia: string;
  esEjemplo: true;
}
