import type { PiezaId } from "@/core/shared/domain/view/pieza.view";

export interface DefinicionPieza {
  id: PiezaId;
  nombre: string;
  pregunta: string;
}

// Receta de 4 piezas, siempre en este orden y con su color fijo.
export const PIEZAS: DefinicionPieza[] = [
  { id: "contexto", nombre: "Contexto", pregunta: "Quién soy y qué estudio" },
  { id: "objetivo", nombre: "Objetivo", pregunta: "Para qué lo necesito" },
  { id: "nivel", nombre: "Nivel", pregunta: "Qué tan profundo" },
  { id: "formato", nombre: "Formato", pregunta: "Cómo lo quiero" },
];

export const nombrePieza = (id: PiezaId): string => PIEZAS.find((pieza) => pieza.id === id)?.nombre ?? id;
