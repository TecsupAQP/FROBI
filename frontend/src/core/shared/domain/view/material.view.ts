export interface Tema {
  id: string;
  numero: number;
  titulo: string;
  textoOriginal: string;
  // «Págs. 4–9» en un PDF; sin páginas en texto pegado.
  paginas?: string;
  // Página del PDF donde empieza, para abrir el documento original ahí.
  paginaInicio?: number;
}

export interface Material {
  id: string;
  titulo: string;
  carrera: string;
  descripcion: string;
  etiquetas: string[];
  minutosLectura: number;
  temas: Tema[];
  // La persona subió un PDF y se puede ver el documento original.
  tieneArchivo: boolean;
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
  origen: "ejemplo" | "pdf" | "texto" | "clase";
  vistaPrevia: string;
  // La que se está estudiando ahora.
  actual: boolean;
  // Solo en el material de la clase: cómo se trabaja y cuánto avanzó la persona.
  enClase?: GuiaDeClase;
}

export interface GuiaDeClase {
  modo: "estudio" | "tareas";
  // 0 a 100: tareas hechas sobre el total, o aciertos de la evaluación final.
  avance: number;
  tareas: { ref: string; numero: number; enunciado: string; hecha: boolean }[];
  evaluacion: { aciertos: number; total: number } | null;
}
