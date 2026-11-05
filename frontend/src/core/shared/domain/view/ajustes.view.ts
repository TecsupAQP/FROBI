// Los 5 interruptores de accesibilidad de Ajustes (Figma · 24).
export type AjusteId = "voz" | "contraste" | "textos-cortos" | "subtitulos" | "botones-grandes";

export type IdiomaId = "es" | "qu" | "ay";

export interface Idioma {
  id: IdiomaId;
  nombre: string;
  detalle?: string;
  disponible: boolean;
}

export interface Ajustes {
  idioma: IdiomaId;
  activos: Record<AjusteId, boolean>;
}
