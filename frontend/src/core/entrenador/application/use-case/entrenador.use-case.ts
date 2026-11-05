import type { EntrenadorPort } from "@/core/entrenador/infraestructure/ports/in/entrenador.port";
import type {
  Autonomia,
  InstruccionMejorada,
  PromptScore,
} from "@/core/shared/domain/view/prompt-score.view";
import type { PiezaId, PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";
import { api } from "@/core/shared/infraestructure/http/api.client";
import type {
  CierreDto,
  ComparacionInstruccionDto,
  EvaluacionInstruccionDto,
} from "@/core/shared/infraestructure/http/api.dto";
import { piezaDesdeApi } from "@/core/shared/infraestructure/http/api.mapper";
import { materialActualId } from "@/core/shared/infraestructure/http/contexto-estudio";
import {
  ORDEN_PIEZAS,
  PLANTILLA_INSTRUCCION,
  construirAutonomia,
  piezasDetectadas,
} from "@/constants/entrenador.constant";

const MENSAJE_NIVEL: Record<number, string> = {
  1: "Con plantilla: completa los espacios de cada pieza.",
  2: "Aquí te damos pistas por pieza, sin escribir por ti.",
  3: "Ya escribes instrucciones completas sin ayuda.",
};

const oraciones = (texto: string): string[] =>
  texto
    .split(/(?<=[.!?])\s+/)
    .map((frase) => frase.trim())
    .filter(Boolean);

// POST /prompt-evaluations y POST /prompt-evaluations/{id}/compare.
export class EntrenadorUseCase implements EntrenadorPort {
  // La comparación se pide sobre la última evaluación.
  private ultima: EvaluacionInstruccionDto | null = null;

  async obtenerAutonomia(): Promise<Autonomia> {
    const cierre = await api.get<CierreDto>("/me/journey-summary").catch(() => null);
    const nivel = cierre?.autonomy_level ?? 1;
    return construirAutonomia(nivel, MENSAJE_NIVEL[nivel] ?? MENSAJE_NIVEL[1]!);
  }

  obtenerPlantilla(): Promise<PiezaInstruccion[]> {
    return Promise.resolve(PLANTILLA_INSTRUCCION);
  }

  async evaluarInstruccion(instruccion: string): Promise<PromptScore> {
    const evaluacion = await api.post<EvaluacionInstruccionDto>("/prompt-evaluations", {
      text: instruccion,
      material_id: await materialActualId().catch(() => null),
    });
    this.ultima = evaluacion;
    // Puntaje de 0 a 4 por pieza: desde 2 la pieza está, aunque se pueda mejorar.
    const piezas = ORDEN_PIEZAS.map((pieza) => {
      const puntaje = evaluacion.scores.find((item) => piezaDesdeApi(item.piece) === pieza);
      return { pieza, presente: (puntaje?.score ?? 0) >= 2, comentario: puntaje?.feedback ?? "" };
    });
    const presentes = piezas.filter((pieza) => pieza.presente).length;
    // El ejemplo es la frase de la versión mejorada que aporta la pieza que más falta.
    const faltante = evaluacion.missing_piece ? piezaDesdeApi(evaluacion.missing_piece) : null;
    const frases = oraciones(evaluacion.improved_text);
    const ejemplo = (faltante && frases.find((frase) => piezasDetectadas(frase).includes(faltante))) || "";
    return {
      instruccion,
      piezas,
      presentes,
      total: piezas.length,
      sugerencia: presentes < piezas.length ? { texto: evaluacion.suggestion, ejemplo } : null,
      autonomia: construirAutonomia(evaluacion.autonomy_level, evaluacion.autonomy_label),
    };
  }

  async mejorarInstruccion(instruccion: string): Promise<InstruccionMejorada> {
    if (!this.ultima || this.ultima.text !== instruccion) await this.evaluarInstruccion(instruccion);
    const evaluacion = this.ultima!;
    const comparacion = await api.post<ComparacionInstruccionDto>(
      `/prompt-evaluations/${evaluacion.id}/compare`,
    );
    // Cada frase de la versión mejorada se marca con la pieza que aporta.
    const receta = oraciones(comparacion.improved.prompt).map<PiezaInstruccion>((frase) => ({
      pieza: (piezasDetectadas(frase)[0] ?? "objetivo") as PiezaId,
      texto: frase,
    }));
    return {
      receta,
      resultado: oraciones(comparacion.improved.output),
      autonomia: construirAutonomia(evaluacion.autonomy_level, evaluacion.autonomy_label),
    };
  }

  contarPiezas(instruccion: string): PiezaId[] {
    return piezasDetectadas(instruccion);
  }
}
