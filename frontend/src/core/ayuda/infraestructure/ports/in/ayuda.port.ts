import type { ResultadoIntento, TareaAyuda } from "@/core/shared/domain/view/ayuda.view";

export interface AyudaPort {
  obtenerTarea(tareaId: string): Promise<TareaAyuda | null>;
  // Revisa el intento propio; la respuesta final solo se muestra después de un intento.
  probarIntento(tareaId: string, intento: string): Promise<ResultadoIntento>;
  obtenerCriteriosSinIa(tareaId: string): Promise<string[]>;
}
