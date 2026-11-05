import type {
  EscalonId,
  EstadoAyuda,
  ResultadoIntento,
  TareaAyuda,
} from "@/core/shared/domain/view/ayuda.view";

export interface IntentoAbierto {
  intentoId: string;
  tarea: TareaAyuda;
  estado: EstadoAyuda;
}

export interface EscalonAbierto {
  contenido: string[];
  estado: EstadoAyuda;
}

export interface IntentoRevisado {
  resultado: ResultadoIntento;
  estado: EstadoAyuda;
}

export interface AyudaPort {
  // Abre un intento nuevo sobre la tarea. null si la tarea no existe.
  abrirIntento(tareaId: string): Promise<IntentoAbierto | null>;
  // Solo se abre el siguiente escalón; la respuesta final, después de un intento propio.
  abrirEscalon(intentoId: string, escalon: EscalonId): Promise<EscalonAbierto>;
  // Compara el intento con la guía, sin IA.
  enviarIntento(intentoId: string, texto: string, criterios?: string[]): Promise<IntentoRevisado>;
  obtenerCriteriosSinIa(tareaId: string): Promise<string[]>;
}
