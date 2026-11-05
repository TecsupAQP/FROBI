import type { ProgresoPort } from "@/core/progreso/infraestructure/ports/in/progreso.port";
import type { Progreso } from "@/core/shared/domain/view/progreso.view";
import { api } from "@/core/shared/infraestructure/http/api.client";
import type { CierreDto, MaterialDto, ProgresoDto } from "@/core/shared/infraestructure/http/api.dto";
import { formatoDesdeApi, nombreFormato } from "@/core/shared/infraestructure/http/api.mapper";
import { materialActualId } from "@/core/shared/infraestructure/http/contexto-estudio";
import { tituloDeGuia } from "@/core/shared/application/util/texto.util";
import { construirAutonomia } from "@/constants/entrenador.constant";

// El puntaje de una instrucción va de 0 a 16 (4 piezas de 0 a 4): se muestra como piezas completas.
const PUNTOS_POR_PIEZA = 4;

// GET /me/progress (estado vacío explícito si aún no hay datos) y /me/journey-summary.
export class ProgresoUseCase implements ProgresoPort {
  async obtenerProgreso(alias: string): Promise<Progreso | null> {
    const [progreso, cierre, material] = await Promise.all([
      api.get<ProgresoDto>("/me/progress"),
      api.get<CierreDto>("/me/journey-summary").catch(() => null),
      materialActualId()
        .then((id) => api.get<MaterialDto>(`/materials/${id}`))
        .catch(() => null),
    ]);
    if (!progreso.has_data) return null;

    const aciertos = progreso.accuracy_by_format.map((dato) => ({
      formato: formatoDesdeApi(dato.format),
      porcentaje: dato.total ? Math.round((dato.correct / dato.total) * 100) : 0,
    }));
    const mejor = [...aciertos].sort((a, b) => b.porcentaje - a.porcentaje)[0];
    const autonomia = construirAutonomia(cierre?.autonomy_level ?? 1, "");
    const nivel = autonomia.niveles.find((item) => item.nivel === autonomia.nivelActual);

    return {
      alias,
      guia: (material && tituloDeGuia(material.title)) ?? "Tu guía",
      mensaje: {
        titulo: progreso.message,
        texto: mejor
          ? `Aciertas el ${mejor.porcentaje} % con ${nombreFormato(mejor.formato)}. Prueba tu próximo tema con ese formato.`
          : "Sigue practicando para ver en qué formato aprendes mejor.",
      },
      temasPracticados: progreso.formats_used.reduce((suma, dato) => suma + dato.count, 0),
      mejorFormato: mejor?.formato ?? "lectura-facil",
      autonomia: `Nivel ${autonomia.nivelActual} · ${nivel?.nombre ?? ""}`,
      aciertos,
      intentos: progreso.prompt_scores.map((punto) => Math.round(punto.total / PUNTOS_POR_PIEZA)),
      resueltosSinIa: progreso.solved_without_ai,
    };
  }
}
