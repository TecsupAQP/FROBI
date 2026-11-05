import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";
import type { PiezaId, PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";
import type { PerfilAccesibilidadId } from "@/core/shared/domain/view/perfil.view";
import type { FormatoApi, PerfilApi, PiezaApi, RecetaDto } from "@/core/shared/infraestructure/http/api.dto";

// Traducciones entre el vocabulario de la API (inglés) y el del front.
const FORMATOS: Record<FormatoApi, FormatoId> = {
  visual_map: "mapa-visual",
  real_example: "ejemplo-real",
  easy_read: "lectura-facil",
  audio: "audio",
};

export const formatoDesdeApi = (formato: FormatoApi): FormatoId => FORMATOS[formato];

export const formatoHaciaApi = (formato: FormatoId): FormatoApi =>
  (Object.keys(FORMATOS) as FormatoApi[]).find((clave) => FORMATOS[clave] === formato) ?? "easy_read";

const PIEZAS: Record<PiezaApi, PiezaId> = {
  context: "contexto",
  goal: "objetivo",
  level: "nivel",
  format: "formato",
};

export const piezaDesdeApi = (pieza: PiezaApi): PiezaId => PIEZAS[pieza];

const NOMBRE_FORMATO: Record<FormatoId, string> = {
  "mapa-visual": "Mapa visual",
  "ejemplo-real": "Ejemplo real",
  "lectura-facil": "Lectura fácil",
  audio: "Audio",
};

export const nombreFormato = (formato: FormatoId): string => NOMBRE_FORMATO[formato];

// La receta de 4 piezas que se mostró es la misma que se envió a la IA.
export const recetaDesdeApi = (receta: RecetaDto): PiezaInstruccion[] => [
  { pieza: "contexto", texto: receta.context },
  { pieza: "objetivo", texto: receta.goal },
  { pieza: "nivel", texto: receta.level },
  { pieza: "formato", texto: NOMBRE_FORMATO[formatoDesdeApi(receta.format)] },
];

// Perfiles del asistente. "Neurodivergencia" agrupa lectura y atención en la API.
const PERFILES: Record<PerfilAccesibilidadId, PerfilApi[]> = {
  "baja-vision": ["low_vision"],
  sordera: ["hearing"],
  neurodivergencia: ["reading", "attention"],
  movilidad: ["motor"],
};

export const perfilesHaciaApi = (perfiles: PerfilAccesibilidadId[]): PerfilApi[] => [
  ...new Set(perfiles.flatMap((perfil) => PERFILES[perfil])),
];

export const perfilesDesdeApi = (perfiles: string[]): PerfilAccesibilidadId[] =>
  (Object.keys(PERFILES) as PerfilAccesibilidadId[]).filter((perfil) =>
    PERFILES[perfil].some((api) => perfiles.includes(api)),
  );
