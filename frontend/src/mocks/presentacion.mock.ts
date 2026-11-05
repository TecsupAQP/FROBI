import type { RouteLocationRaw } from "vue-router";
import type { NombreIcono } from "@/constants/iconos.constant";
import { RutaEnum, TAREA_EJEMPLO } from "@/enums/ruta.enum";

export interface PasoRecorrido {
  numero: number;
  quien: "docente" | "estudiante" | "ambos";
  etiqueta: string;
  titulo: string;
  texto: string;
  enlace: string;
  destino: RouteLocationRaw;
}

// Recorrido de 9 pasos (Figma · 21). Nombres y datos de ejemplo.
export const RECORRIDO_MOCK: PasoRecorrido[] = [
  {
    numero: 1,
    quien: "docente",
    etiqueta: "Docente",
    titulo: "Elige su rol y crea su cuenta",
    texto: "Marisol elige «Soy docente».",
    enlace: "Elegir rol",
    destino: { name: RutaEnum.ROL },
  },
  {
    numero: 2,
    quien: "ambos",
    etiqueta: "Docente y estudiante",
    titulo: "Hace la introducción a la IA",
    texto: "Tres ideas en menos de un minuto. Se puede omitir.",
    enlace: "Introducción",
    destino: { name: RutaEnum.INTRO },
  },
  {
    numero: 3,
    quien: "docente",
    etiqueta: "Docente",
    titulo: "Crea la clase y sube su guía",
    texto: "«Sensores industriales» con 2 archivos y reglas de ayuda.",
    enlace: "Crear clase",
    destino: { name: RutaEnum.CLASE_NUEVA },
  },
  {
    numero: 4,
    quien: "docente",
    etiqueta: "Docente",
    titulo: "Invita a Ana y a Luis",
    texto: "Con código o enlace. Ana se une; Luis queda pendiente.",
    enlace: "Invitar",
    destino: { name: RutaEnum.CLASE_INVITAR },
  },
  {
    numero: 5,
    quien: "estudiante",
    etiqueta: "Estudiante",
    titulo: "Ana entra con el código y elige cómo aprende",
    texto: "Perfil de accesibilidad: lectura fácil y textos cortos.",
    enlace: "Login y accesibilidad",
    destino: { name: RutaEnum.PERFIL_ACCESIBILIDAD },
  },
  {
    numero: 6,
    quien: "estudiante",
    etiqueta: "Estudiante",
    titulo: "Aprende con la escalera de ayuda",
    texto: "Pista, pista, paso a paso; la respuesta llega al final.",
    enlace: "Escalera",
    destino: { name: RutaEnum.AYUDA, params: { tarea: TAREA_EJEMPLO } },
  },
  {
    numero: 7,
    quien: "estudiante",
    etiqueta: "Estudiante",
    titulo: "Practica sin IA",
    texto: "Resuelve solo, se autoevalúa y cuenta como logro.",
    enlace: "Sin IA",
    destino: { name: RutaEnum.SIN_IA, params: { tarea: TAREA_EJEMPLO } },
  },
  {
    numero: 8,
    quien: "docente",
    etiqueta: "Docente",
    titulo: "Ve el avance de la clase",
    texto: "Ana va bien; Luis se traba en la pista 1.",
    enlace: "Panel docente",
    destino: { name: RutaEnum.DOCENTE },
  },
  {
    numero: 9,
    quien: "docente",
    etiqueta: "Docente",
    titulo: "Abre el detalle de Ana",
    texto: "Ve su uso de ayudas, competencias y qué proponerle.",
    enlace: "Detalle",
    destino: { name: RutaEnum.ALUMNO, params: { alias: "ana" } },
  },
];

export type TipoPantallaPersona = "voz" | "pasos" | "transcripcion" | "teclado" | "acompanante";

export interface PersonaEjemplo {
  id: string;
  perfil: string;
  icono: NombreIcono;
  nombre: string;
  situacion: string;
  pantalla: TipoPantallaPersona;
  cambios: string[];
  quienAyuda: string;
}

// Un mismo sistema, distintas personas (Figma · 23). Personas y casos inventados.
export const PERSONAS_MOCK: PersonaEjemplo[] = [
  {
    id: "rosa",
    perfil: "Ceguera o baja visión",
    icono: "eye",
    nombre: "Rosa (ejemplo)",
    situacion: "Usa lector de pantalla y prepara un informe.",
    pantalla: "voz",
    cambios: [
      "Cada paso se lee en voz alta",
      "Mapa visual descrito en texto",
      "Alto contraste, letra grande y etiquetas para lector de pantalla",
    ],
    quienAyuda: "Se configura sola con la pregunta en voz alta.",
  },
  {
    id: "diego",
    perfil: "Neurodivergencia (dislexia, TDAH, autismo)",
    icono: "type",
    nombre: "Diego (ejemplo)",
    situacion: "Se distrae con pantallas llenas.",
    pantalla: "pasos",
    cambios: [
      "Una pista por pantalla",
      "Lectura fácil y frases cortas",
      "Sin límite de tiempo ni avisos que distraigan",
    ],
    quienAyuda: "Puede pedir a su docente que active la configuración.",
  },
  {
    id: "elena",
    perfil: "Sordera o hipoacusia",
    icono: "captions",
    nombre: "Elena (ejemplo)",
    situacion: "No usa audio.",
    pantalla: "transcripcion",
    cambios: [
      "Todo audio tiene transcripción",
      "Instrucciones siempre por escrito",
      "Lengua de señas: queda como visión",
    ],
    quienAyuda: "Se configura sola.",
  },
  {
    id: "marco",
    perfil: "Movilidad reducida",
    icono: "hand",
    nombre: "Marco (ejemplo)",
    situacion: "Usa solo teclado.",
    pantalla: "teclado",
    cambios: ["Botones grandes", "Todo se maneja con teclado", "Sin gestos finos ni límite de tiempo"],
    quienAyuda: "Un familiar puede configurarlo; después usa solo.",
  },
  {
    id: "pedro",
    perfil: "Con acompañante",
    icono: "users",
    nombre: "Don Pedro y su nieta Lucía (ejemplo)",
    situacion: "Don Pedro no maneja bien el celular.",
    pantalla: "acompanante",
    cambios: ["La nieta responde el asistente por él", "Él aprende por su cuenta", "Ella no ve su progreso"],
    quienAyuda: "Una persona de confianza, solo en la configuración.",
  },
];
