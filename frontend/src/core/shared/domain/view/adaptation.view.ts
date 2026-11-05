import type { PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";

export type FormatoId = "mapa-visual" | "ejemplo-real" | "lectura-facil" | "audio";

export interface NodoConcepto {
  titulo: string;
  detalle: string;
}

export interface ContenidoMapaVisual {
  formato: "mapa-visual";
  conceptoCentral: string;
  nodos: NodoConcepto[];
  // Vacío si el material no dice para qué se usa.
  usos: string;
}

export interface ContenidoEjemploReal {
  formato: "ejemplo-real";
  pasos: string[];
  advertencia: string;
  // La ilustración de la faja con botellas solo acompaña ejemplos de envasado.
  conIlustracion: boolean;
}

export interface TerminoGlosario {
  termino: string;
  definicion: string;
}

export interface ContenidoLecturaFacil {
  formato: "lectura-facil";
  frases: string[];
  glosario: TerminoGlosario[];
}

export interface ContenidoAudio {
  formato: "audio";
  titulo: string;
  voz: string;
  duracionSegundos: number;
  posicionSegundos: number;
  frases: string[];
  fraseActual: number;
}

export type ContenidoAdaptado =
  | ContenidoMapaVisual
  | ContenidoEjemploReal
  | ContenidoLecturaFacil
  | ContenidoAudio;

export interface Adaptation {
  materialId: string;
  temaId: string;
  ruta: string[];
  titulo: string;
  receta: PiezaInstruccion[];
  contenido: ContenidoAdaptado;
  // true cuando la IA no respondió y se muestra una versión preparada sin IA (RNF06)
  esRespaldo: boolean;
  // Aviso de la API sobre el uso de la IA (o sobre la versión sin IA).
  aviso: string;
  // La instrucción completa enviada a la IA, para "Copiar receta".
  instruccion: string;
}
