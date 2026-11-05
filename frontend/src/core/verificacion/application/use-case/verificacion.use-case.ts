import type {
  RespuestaRevisada,
  VerificacionPort,
} from "@/core/verificacion/infraestructure/ports/in/verificacion.port";
import type { Verificacion } from "@/core/shared/domain/view/pregunta.view";
import { api } from "@/core/shared/infraestructure/http/api.client";
import type {
  AdaptacionDto,
  PreguntaDto,
  RespuestaPreguntaDto,
} from "@/core/shared/infraestructure/http/api.dto";
import { formatoDesdeApi } from "@/core/shared/infraestructure/http/api.mapper";
import { adaptacionActualId } from "@/core/shared/infraestructure/http/contexto-estudio";

const LETRAS = ["A", "B", "C", "D", "E"];

// POST /adaptations/{id}/questions y POST /questions/{id}/answers.
export class VerificacionUseCase implements VerificacionPort {
  async obtenerVerificacion(): Promise<Verificacion> {
    const adaptacionId = await adaptacionActualId();
    const [adaptacion, preguntas] = await Promise.all([
      api.get<AdaptacionDto>(`/adaptations/${adaptacionId}`),
      api.post<PreguntaDto[]>(`/adaptations/${adaptacionId}/questions`),
    ]);
    const formato = formatoDesdeApi(adaptacion.format);
    return {
      ruta: [adaptacion.content.title, "Comprueba lo que aprendiste"],
      // La respuesta correcta y la explicación llegan al responder.
      preguntas: preguntas.map((pregunta) => ({
        id: pregunta.id,
        enunciado: pregunta.statement,
        opciones: pregunta.options.map((opcion, indice) => ({
          id: opcion.id,
          letra: LETRAS[indice] ?? opcion.id.toUpperCase(),
          texto: opcion.text,
        })),
        correcta: "",
        explicacionAcierto: "",
        explicacionError: "",
        formatoSugerido: formato,
      })),
    };
  }

  async comprobarRespuesta(preguntaId: string, opcionId: string): Promise<RespuestaRevisada> {
    const respuesta = await api.post<RespuestaPreguntaDto>(`/questions/${preguntaId}/answers`, {
      option: opcionId,
    });
    return {
      correcta: respuesta.is_correct,
      opcionCorrecta: respuesta.correct_option,
      explicacion: respuesta.feedback,
      formatoSugerido: respuesta.suggested_format ? formatoDesdeApi(respuesta.suggested_format) : null,
    };
  }
}
