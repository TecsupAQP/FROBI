import type { ObtenerAdaptacionPort } from "@/core/adaptacion/infraestructure/ports/in/obtener-adaptacion.port";
import type { Adaptation, ContenidoAdaptado, FormatoId } from "@/core/shared/domain/view/adaptation.view";
import { api } from "@/core/shared/infraestructure/http/api.client";
import type { AdaptacionDto } from "@/core/shared/infraestructure/http/api.dto";
import {
  formatoDesdeApi,
  formatoHaciaApi,
  nombreFormato,
  recetaDesdeApi,
} from "@/core/shared/infraestructure/http/api.mapper";
import { materialActualId, recordarAdaptacion } from "@/core/shared/infraestructure/http/contexto-estudio";
import { numeroDeTema } from "@/core/shared/application/util/texto.util";

const PALABRAS_POR_SEGUNDO = 2.5;

const oraciones = (texto: string): string[] =>
  texto
    .split(/(?<=[.!?])\s+/)
    .map((frase) => frase.trim())
    .filter(Boolean);

const conPunto = (texto: string) => (/[.!?]$/.test(texto) ? texto : `${texto}.`);

// La API entrega secciones (título, texto y puntos); cada formato las muestra a su manera.
function contenidoDesdeApi(formato: FormatoId, dto: AdaptacionDto): ContenidoAdaptado {
  const { title, sections, plain_text: textoPlano } = dto.content;
  switch (formato) {
    case "mapa-visual":
      return {
        formato,
        conceptoCentral: title,
        nodos: sections.map((seccion) => ({
          titulo: seccion.heading,
          detalle: seccion.body,
          puntos: seccion.items,
        })),
        usos: "",
      };
    case "ejemplo-real":
      return {
        formato,
        pasos: sections.map((seccion) => `${conPunto(seccion.heading)} ${seccion.body}`.trim()),
        advertencia: "",
        conIlustracion: /botell/i.test(textoPlano),
      };
    case "lectura-facil": {
      // Los puntos "Palabra: explicación" forman el glosario.
      const glosario = sections
        .flatMap((seccion) => seccion.items)
        .map((item) => item.match(/^([^:]{2,40}):\s*(.+)$/))
        .filter((partes): partes is RegExpMatchArray => partes !== null)
        .map((partes) => ({ termino: partes[1]?.trim() ?? "", definicion: partes[2]?.trim() ?? "" }));
      return {
        formato,
        frases: sections.flatMap((seccion) => oraciones(seccion.body)),
        glosario,
      };
    }
    case "audio": {
      // La voz es del navegador: la API entrega el texto que se lee.
      const frases = oraciones(textoPlano);
      return {
        formato,
        titulo: `${title} · Audio`,
        voz: "Voz en español del navegador",
        duracionSegundos: Math.round(textoPlano.split(/\s+/).length / PALABRAS_POR_SEGUNDO),
        posicionSegundos: 0,
        frases,
        fraseActual: 0,
      };
    }
  }
}

// POST /materials/{id}/adaptations: tope de 15 s en la API, con una versión sin IA de respaldo.
export class ObtenerAdaptacionUseCase implements ObtenerAdaptacionPort {
  async obtenerAdaptacion(temaId: string, formato: FormatoId): Promise<Adaptation> {
    const materialId = await materialActualId();
    // La IA solo lee este tema: un PDF largo cuesta lo mismo por petición que uno corto.
    const dto = await api.post<AdaptacionDto>(`/materials/${materialId}/adaptations`, {
      format: formatoHaciaApi(formato),
      topic: numeroDeTema(temaId),
    });
    // La escalera de ayuda y las preguntas se piden sobre esta adaptación.
    recordarAdaptacion(dto.id);
    const formatoRecibido = formatoDesdeApi(dto.format);
    return {
      materialId,
      temaId,
      ruta: [dto.content.title, nombreFormato(formatoRecibido)],
      titulo: dto.content.title,
      receta: recetaDesdeApi(dto.recipe),
      contenido: contenidoDesdeApi(formatoRecibido, dto),
      esRespaldo: dto.fallback,
      aviso: dto.ai_notice,
      instruccion: dto.prompt_text,
    };
  }
}
