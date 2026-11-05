import type { Tema } from "@/core/shared/domain/view/material.view";
import type { MaterialDto } from "@/core/shared/infraestructure/http/api.dto";

// "motores-electricos.pdf" → "Motores electricos"
export const tituloDesdeArchivo = (nombre: string): string => {
  const limpio = nombre
    .replace(/\.pdf$/i, "")
    .replace(/[-_]+/g, " ")
    .trim();
  return limpio.charAt(0).toUpperCase() + limpio.slice(1);
};

// "Guía de sensores industriales" → "Sensores industriales"
export const tituloDeGuia = (titulo: string): string => {
  const sinPrefijo = titulo.replace(/^Guía de\s+/i, "").trim();
  return sinPrefijo.charAt(0).toUpperCase() + sinPrefijo.slice(1);
};

const paginasDe = (inicio: number | null, fin: number | null): string | undefined => {
  if (inicio === null) return undefined;
  return fin === null || fin === inicio ? `Pág. ${inicio}` : `Págs. ${inicio}–${fin}`;
};

const sinTitulo = (texto: string, titulo: string): string =>
  texto.toLowerCase().startsWith(titulo.toLowerCase()) ? texto.slice(titulo.length).trim() || texto : texto;

// Los temas que arma la API; si no vienen (API anterior), se dividen por los "## Título".
export function temasDeMaterial(dto: MaterialDto): Tema[] {
  if (!dto.topics?.length) return temasDesdeTexto(dto.extracted_text);
  return dto.topics.map((tema) => ({
    id: `tema-${tema.position}`,
    numero: tema.position,
    titulo: tema.title,
    // El texto del tema empieza con su título (es la línea del PDF): no se repite.
    textoOriginal: sinTitulo(tema.text.replace(/\s+/g, " ").trim(), tema.title),
    paginas: paginasDe(tema.page_start, tema.page_end),
    paginaInicio: tema.page_start ?? undefined,
  }));
}

// El número de tema que espera la API a partir del id «tema-N».
export const numeroDeTema = (temaId: string): number | undefined => {
  const numero = Number(temaId.replace(/^tema-/, ""));
  return Number.isInteger(numero) && numero > 0 ? numero : undefined;
};

// El texto extraído usa "## Título" para cada sección: cada una es un tema de la guía.
export function temasDesdeTexto(texto: string): Tema[] {
  const bloques = texto
    .split(/^##\s+/m)
    .map((bloque) => bloque.trim())
    .filter(Boolean);
  const conTitulo = /^##\s+/m.test(texto);
  return bloques.map((bloque, indice) => {
    const [primera = "", ...resto] = bloque.split("\n");
    return {
      id: `tema-${indice + 1}`,
      numero: indice + 1,
      titulo: conTitulo ? primera.trim() : bloques.length === 1 ? "Todo el material" : `Parte ${indice + 1}`,
      textoOriginal: (conTitulo ? resto.join(" ") : bloque).replace(/\s+/g, " ").trim(),
    };
  });
}
