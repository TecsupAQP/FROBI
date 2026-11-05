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
