import type { CierrePort } from "@/core/cierre/infraestructure/ports/in/cierre.port";
import type { ResumenCierre } from "@/core/shared/domain/view/cierre.view";
import { api } from "@/core/shared/infraestructure/http/api.client";
import type { CierreDto, MaterialDto } from "@/core/shared/infraestructure/http/api.dto";
import { formatoDesdeApi, recetaDesdeApi } from "@/core/shared/infraestructure/http/api.mapper";
import { materialActualId } from "@/core/shared/infraestructure/http/contexto-estudio";
import { tituloDeGuia } from "@/core/shared/application/util/texto.util";
import { ORDEN_PIEZAS, construirAutonomia } from "@/constants/entrenador.constant";

const PUNTOS_POR_PIEZA = 4;

// GET /me/journey-summary: formato, receta aprendida, mejor puntaje y autonomía.
export class CierreUseCase implements CierrePort {
  async obtenerResumen(): Promise<ResumenCierre> {
    const [cierre, material] = await Promise.all([
      api.get<CierreDto>("/me/journey-summary"),
      materialActualId()
        .then((id) => api.get<MaterialDto>(`/materials/${id}`))
        .catch(() => null),
    ]);
    const logradas = Math.round((cierre.best_prompt_score ?? 0) / PUNTOS_POR_PIEZA);
    const autonomia = construirAutonomia(cierre.autonomy_level ?? 1, cierre.message);
    const nivel = autonomia.niveles.find((item) => item.nivel === autonomia.nivelActual);
    return {
      tema: (material && tituloDeGuia(material.title)) ?? "Tu guía",
      receta: cierre.learned_recipe ? recetaDesdeApi(cierre.learned_recipe) : [],
      formatoUsado: cierre.favorite_format ? formatoDesdeApi(cierre.favorite_format) : "lectura-facil",
      piezasLogradas: ORDEN_PIEZAS.slice(0, Math.min(ORDEN_PIEZAS.length, logradas)),
      totalPiezas: ORDEN_PIEZAS.length,
      autonomia: {
        nivel: autonomia.nivelActual,
        total: 3,
        nombre: nivel?.nombre ?? "",
        mensaje: cierre.message,
      },
    };
  }
}
