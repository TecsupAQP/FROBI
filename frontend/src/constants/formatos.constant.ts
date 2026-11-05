import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";
import type { NombreIcono } from "@/constants/iconos.constant";

export interface DefinicionFormato {
  id: FormatoId;
  nombre: string;
  nombreCorto: string;
  descripcion: string;
  icono: NombreIcono;
}

// Botones de formato: no usan los colores de las piezas.
export const FORMATOS: DefinicionFormato[] = [
  {
    id: "mapa-visual",
    nombre: "Mapa visual",
    nombreCorto: "Mapa visual",
    descripcion: "Ve cómo se conectan los conceptos",
    icono: "map",
  },
  {
    id: "ejemplo-real",
    nombre: "Ejemplo de la vida real",
    nombreCorto: "Ejemplo real",
    descripcion: "Entiéndelo con un caso de fábrica",
    icono: "bulb",
  },
  {
    id: "lectura-facil",
    nombre: "Lectura fácil",
    nombreCorto: "Lectura fácil",
    descripcion: "Frases cortas y palabras simples",
    icono: "book",
  },
  {
    id: "audio",
    nombre: "Audio",
    nombreCorto: "Audio",
    descripcion: "Escúchalo mientras repasas",
    icono: "audio",
  },
];

export const esFormatoValido = (valor: unknown): valor is FormatoId =>
  typeof valor === "string" && FORMATOS.some((formato) => formato.id === valor);
