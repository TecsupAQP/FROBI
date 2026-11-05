import type { RecomendacionHerramientas } from "@/core/shared/domain/view/tool.view";

export interface AfirmacionRevisada {
  id: string;
  texto: string;
}

export interface HerramientasPort {
  // Sin afirmación revisada, se recomienda según la necesidad "verificar una fuente".
  obtenerRecomendacion(afirmacion: AfirmacionRevisada | null): Promise<RecomendacionHerramientas>;
}
