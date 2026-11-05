import type { Ajustes } from "@/core/shared/domain/view/ajustes.view";
import type { Perfil } from "@/core/shared/domain/view/perfil.view";

// Valores con los que arranca la app antes de leer la API.
export const PERFIL_INICIAL: Perfil = {
  modo: null,
  codigoClase: null,
  perfiles: [],
  configuradoPor: "yo",
  vioIntro: false,
  vioAsistente: false,
};

export const AJUSTES_INICIALES: Ajustes = {
  idioma: "es",
  activos: {
    voz: false,
    contraste: false,
    "textos-cortos": false,
    subtitulos: false,
    "botones-grandes": false,
  },
};

// Detalle que el front agrega a cada idioma de la API.
export const DETALLE_IDIOMA: Record<string, string> = {
  es: "Idioma actual",
  qu: "Quechua sureño",
};
