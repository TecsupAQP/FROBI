import type { AjusteId } from "@/core/shared/domain/view/ajustes.view";
import type { PerfilAccesibilidadId } from "@/core/shared/domain/view/perfil.view";
import type { NombreIcono } from "@/constants/iconos.constant";

export interface DefinicionPerfil {
  id: PerfilAccesibilidadId;
  nombre: string;
  descripcion: string;
  icono: NombreIcono;
  // Ajustes que se encienden al elegir este perfil.
  ajustes: AjusteId[];
  // Lo que cambia en pantalla ("Así cambiará tu pantalla").
  cambios: string[];
}

// Figma · 17 (paso 5). "Español como segunda lengua" queda fuera: está pendiente de eliminarse.
export const PERFILES_ACCESIBILIDAD: DefinicionPerfil[] = [
  {
    id: "baja-vision",
    nombre: "Ceguera o baja visión",
    descripcion: "Audio, alto contraste y letra grande.",
    icono: "eye",
    ajustes: ["voz", "contraste"],
    cambios: ["Formato por defecto: audio", "Letra grande y alto contraste"],
  },
  {
    id: "sordera",
    nombre: "Sordera o hipoacusia",
    descripcion: "Transcripción de todo el audio y nada de sonido obligatorio.",
    icono: "headphones",
    ajustes: ["subtitulos"],
    cambios: ["Texto de todo lo que se dice", "Nada de sonido obligatorio"],
  },
  {
    id: "neurodivergencia",
    nombre: "Neurodivergencia (dislexia, TDAH, autismo)",
    descripcion: "Lectura fácil, frases cortas y un paso a la vez.",
    icono: "type",
    ajustes: ["textos-cortos"],
    cambios: [
      "Formato por defecto: lectura fácil",
      "Instrucciones en pasos cortos",
      "Glosario de términos siempre visible",
    ],
  },
  {
    id: "movilidad",
    nombre: "Movilidad reducida",
    descripcion: "Botones grandes, atajos de teclado y sin límite de tiempo.",
    icono: "hand",
    ajustes: ["botones-grandes"],
    cambios: ["Botones grandes y atajos de teclado"],
  },
];

export interface DefinicionAjuste {
  id: AjusteId;
  nombre: string;
  // Texto corto del asistente (Figma · 22, paso 2).
  nombreAsistente: string;
  descripcionAsistente: string;
  icono: NombreIcono;
  // Línea de "Lo que activamos" (paso 3).
  resumen: string;
}

// Figma · 24 y 22. "Español sencillo" queda fuera: está pendiente de eliminarse.
export const AJUSTES_ACCESIBILIDAD: DefinicionAjuste[] = [
  {
    id: "voz",
    nombre: "La voz lee cada paso",
    nombreAsistente: "Escuchar",
    descripcionAsistente: "La voz lee todo por ti.",
    icono: "headphones",
    resumen: "Audio: la voz lee cada paso.",
  },
  {
    id: "contraste",
    nombre: "Letra grande y alto contraste",
    nombreAsistente: "Letra grande y alto contraste",
    descripcionAsistente: "Para ver mejor.",
    icono: "eye",
    resumen: "Letra grande y alto contraste.",
  },
  {
    id: "textos-cortos",
    nombre: "Textos cortos, un paso a la vez",
    nombreAsistente: "Textos cortos, un paso a la vez",
    descripcionAsistente: "Sin distracciones.",
    icono: "type",
    resumen: "Textos cortos, una pista por pantalla.",
  },
  {
    id: "subtitulos",
    nombre: "Ver el texto de lo que se dice",
    nombreAsistente: "Ver el texto de lo que se dice",
    descripcionAsistente: "Todo el audio con texto.",
    icono: "captions",
    resumen: "Texto de todo lo que se dice.",
  },
  {
    id: "botones-grandes",
    nombre: "Botones grandes y teclado",
    nombreAsistente: "Botones grandes y teclado",
    descripcionAsistente: "Sin gestos finos.",
    icono: "hand",
    resumen: "Botones grandes y atajos de teclado.",
  },
];
