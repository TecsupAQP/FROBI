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
import type { MaterialClaseDto, MaterialDto } from "@/core/shared/infraestructure/http/api.dto";
import { claseActualId } from "@/core/shared/infraestructure/http/clase-actual";
import {
  adaptacionActualId,
  elegirMaterial,
  materialActualId,
} from "@/core/shared/infraestructure/http/contexto-estudio";
import { temasDesdeTexto, tituloDeGuia } from "@/core/shared/application/util/texto.util";
import { CRITERIOS_SIN_IA, ESCALONES_AYUDA } from "@/constants/tareas.constant";

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
  // La tarea es explicar un tema de la guía actual (tareaId = "tema-N") o una tarea que dejó el
  // docente en una guía de la clase (tareaId = "tarea-{id}").
  async abrirIntento(tareaId: string): Promise<IntentoAbierto | null> {
    if (tareaId.startsWith("tarea-")) return this.abrirTareaDeClase(tareaId);
    const material = await api.get<MaterialDto>(`/materials/${await materialActualId()}`);
    const temas = temasDesdeTexto(material.extracted_text);
    const tema = temas.find((item) => item.id === tareaId);
    if (!tema) return null;
    const intento = await api.post<IntentoAyudaDto>("/help-attempts", {
      adaptation_id: await adaptacionActualId(),
      task_ref: tareaId,
    });
    // Una guía sin secciones tiene un solo tema: se nombra con el título de la guía.
    const nombre = temas.length === 1 ? tituloDeGuia(material.title) : tema.titulo;
    return {
      intentoId: intento.id,
      tarea: {
        id: tareaId,
        ruta: [tituloDeGuia(material.title), `Tema ${tema.numero} de ${temas.length}`],
        titulo: `Explica «${nombre}» con tus palabras`,
        enunciado: `Según tu guía, ¿qué es «${nombre}» y para qué sirve? Respóndelo con tus palabras y, si puedes, con un ejemplo.`,
        escalones: structuredClone(ESCALONES_AYUDA),
      },
      estado: estadoDesdeApi(intento),
    };
  }

  private async abrirTareaDeClase(tareaId: string): Promise<IntentoAbierto | null> {
    const claseId = await claseActualId();
    if (!claseId) return null;
    const guias = await api.get<MaterialClaseDto[]>(`/classes/${claseId}/materials`);
    const guia = guias.find((item) => item.tasks.some((tarea) => tarea.task_ref === tareaId));
    const tarea = guia?.tasks.find((item) => item.task_ref === tareaId);
    if (!guia || !tarea) return null;
    // La tarea se resuelve sobre su guía: la adaptación queda atada a ese material.
    elegirMaterial(guia.id);
    const intento = await api.post<IntentoAyudaDto>("/help-attempts", {
      adaptation_id: await adaptacionActualId(),
      task_ref: tareaId,
    });
    return {
      intentoId: intento.id,
      tarea: {
        id: tareaId,
        ruta: [tituloDeGuia(guia.title), `Tarea ${tarea.position} de ${guia.tasks.length}`],
        titulo: tarea.statement,
        enunciado: tarea.statement,
        escalones: structuredClone(ESCALONES_AYUDA),
      },
      estado: estadoDesdeApi(intento),
    };
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
