export interface Tema {
  id: string;
  numero: number;
  titulo: string;
  textoOriginal: string;
}

export interface Material {
  id: string;
  titulo: string;
  carrera: string;
  descripcion: string;
  etiquetas: string[];
  minutosLectura: number;
  temas: Tema[];
}

// Resultado de leer un PDF subido: se muestra para que la persona lo revise.
export interface ArchivoLeido {
  // Material creado en la API con el texto extraído.
  materialId: string;
  nombre: string;
  paginas?: number;
  tamanoMb: number;
  vistaPrevia: { titulo: string; texto: string };
  // Todo el texto extraído (por ejemplo, para usarlo como borrador).
  texto: string;
}

// Estados del modal de subida (Figma · 4 y 13): elegir → subiendo → listo | error.
export type FaseSubida = "elegir" | "subiendo" | "listo" | "error";

// Una guía de la lista "Mis guías": las que subió o pegó la persona y las de ejemplo.
export interface GuiaResumen {
  id: string;
  titulo: string;
  origen: "ejemplo" | "pdf" | "texto";
  vistaPrevia: string;
  // La que se está estudiando ahora.
  actual: boolean;
}
