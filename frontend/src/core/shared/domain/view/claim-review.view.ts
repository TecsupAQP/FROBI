// Semáforo de afirmaciones. Nunca se dice "falso": FROBI no es un detector.
export type EstadoAfirmacion = "con-respaldo" | "no-comprobable" | "contradice";

export interface ClaimReview {
  id: string;
  texto: string;
  estado: EstadoAfirmacion;
  // Cita de la guía que respalda o contradice la afirmación.
  citaGuia?: string;
  motivo: string;
}

export interface SeccionRevisada {
  id: string;
  numero: number;
  titulo: string;
  // Texto sin afirmaciones marcadas (se muestra tal cual).
  texto?: string;
  afirmaciones: ClaimReview[];
  // Etiqueta de la sección cuando no hay afirmaciones por revisar.
  estadoSeccion?: { estado: EstadoAfirmacion; texto: string };
}

export interface WorkReview {
  consigna: string;
  secciones: SeccionRevisada[];
  resumen: Record<EstadoAfirmacion, number>;
}

export interface BorradorTrabajo {
  consigna: string;
  borrador: string;
}
