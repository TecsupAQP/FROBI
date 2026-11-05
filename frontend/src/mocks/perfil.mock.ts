import type { Ajustes, Idioma } from "@/core/shared/domain/view/ajustes.view";
import type { Perfil } from "@/core/shared/domain/view/perfil.view";

// Código de clase de ejemplo con el que el mock valida (Figma · 18).
export const CODIGO_CLASE_EJEMPLO = "SENS-4821";
export const NOMBRE_CLASE_EJEMPLO = "Sensores industriales";

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

// Quechua y aimara se agregan con revisión de hablantes: por ahora no hay textos en esos idiomas.
export const IDIOMAS_MOCK: Idioma[] = [
  { id: "es", nombre: "Español", detalle: "Idioma actual", disponible: true },
  { id: "qu", nombre: "Quechua", detalle: "Quechua sureño", disponible: false },
  { id: "ay", nombre: "Aimara", disponible: false },
];
