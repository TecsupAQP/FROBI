import type {
  AyudaPort,
  EscalonAbierto,
  IntentoAbierto,
  IntentoRevisado,
} from "@/core/ayuda/infraestructure/ports/in/ayuda.port";
import type { EscalonId, EstadoAyuda } from "@/core/shared/domain/view/ayuda.view";
import { api } from "@/core/shared/infraestructure/http/api.client";
import type {
  EscalonApi,
  EscalonDto,
  IntentoAyudaDto,
  RespuestaPropiaDto,
} from "@/core/shared/infraestructure/http/api.dto";
import { adaptacionActualId } from "@/core/shared/infraestructure/http/contexto-estudio";
import { CRITERIOS_SIN_IA, TAREAS } from "@/constants/tareas.constant";

const ESCALONES: Record<EscalonId, EscalonApi> = {
  "pista-1": "hint_1",
  "pista-2": "hint_2",
  "paso-a-paso": "step_by_step",
  respuesta: "final",
};

const escalonDesdeApi = (paso: IntentoAyudaDto["max_step"]): EscalonId | null =>
  paso === "none"
    ? null
    : ((Object.keys(ESCALONES) as EscalonId[]).find((id) => ESCALONES[id] === paso) ?? null);

const estadoDesdeApi = (intento: IntentoAyudaDto): EstadoAyuda => ({
  alcanzado: escalonDesdeApi(intento.max_step),
  respuestaDesbloqueada: intento.final_unlocked,
  nivel: intento.help_label,
  resueltoSinIa: intento.solved_without_ai,
});

// "1. Lee… 2. Subraya…" se muestra como una línea por paso.
const enLineas = (texto: string): string[] =>
  texto
    .split(/\s(?=\d+\.\s)/)
    .map((linea) => linea.trim())
    .filter(Boolean);

// POST /help-attempts, /help-attempts/{id}/steps y /help-attempts/{id}/own-answer.
export class AyudaUseCase implements AyudaPort {
  async abrirIntento(tareaId: string): Promise<IntentoAbierto | null> {
    const tarea = TAREAS[tareaId];
    if (!tarea) return null;
    const intento = await api.post<IntentoAyudaDto>("/help-attempts", {
      adaptation_id: await adaptacionActualId(),
      task_ref: tareaId,
    });
    return { intentoId: intento.id, tarea: structuredClone(tarea), estado: estadoDesdeApi(intento) };
  }

  async abrirEscalon(intentoId: string, escalon: EscalonId): Promise<EscalonAbierto> {
    const paso = await api.post<EscalonDto>(`/help-attempts/${intentoId}/steps`, {
      step: ESCALONES[escalon],
    });
    return { contenido: enLineas(paso.content), estado: estadoDesdeApi(paso.attempt) };
  }

  async enviarIntento(intentoId: string, texto: string, criterios: string[] = []): Promise<IntentoRevisado> {
    const revision = await api.post<RespuestaPropiaDto>(`/help-attempts/${intentoId}/own-answer`, {
      answer: texto,
      self_check: criterios,
    });
    const pasajes = revision.matching_passages.map((pasaje) => pasaje.text);
    const correcto = pasajes.length > 0;
    return {
      resultado: {
        correcto,
        pasajes,
        comentario: correcto
          ? "Tu guía respalda lo que escribiste. Compáralo con la respuesta final."
          : "No encontramos eso en tu guía. Compara tu intento con la respuesta final.",
      },
      estado: estadoDesdeApi(revision.attempt),
    };
  }

  // La autoevaluación es una lista fija del front: la API solo guarda lo que se marcó.
  obtenerCriteriosSinIa(_tareaId: string): Promise<string[]> {
    return Promise.resolve(CRITERIOS_SIN_IA);
  }
}
