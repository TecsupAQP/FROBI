import type { Progreso } from "@/core/shared/domain/view/progreso.view";

export interface ProgresoPort {
  // null cuando todavía no hay ninguna respuesta (estado vacío).
  obtenerProgreso(alias: string): Promise<Progreso | null>;
}
