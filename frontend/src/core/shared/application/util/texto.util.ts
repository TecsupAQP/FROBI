import type { Tema } from "@/core/shared/domain/view/material.view";

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
