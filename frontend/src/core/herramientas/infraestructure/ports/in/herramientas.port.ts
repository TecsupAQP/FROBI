import type { RecomendacionHerramientas } from "@/core/shared/domain/view/tool.view";

export interface HerramientasPort {
  obtenerRecomendacion(afirmacionId: string): Promise<RecomendacionHerramientas>;
}
