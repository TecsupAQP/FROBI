import type { RouteLocationRaw } from "vue-router";
import { RutaEnum, TAREA_EJEMPLO } from "@/enums/ruta.enum";

export interface PasoRecorrido {
  titulo: string;
  texto: string;
  // Pantalla del paso; sin destino, el paso se muestra donde esté la persona.
  destino?: RouteLocationRaw;
  // Ruta en la que se espera estar (si la app redirige, el paso se muestra sin resaltar).
  ruta?: RutaEnum;
  // Valor de data-recorrido de la parte que se resalta.
  objetivo?: string;
  // Texto que se muestra si la parte no está en pantalla (por ejemplo, sin guía todavía).
  siFalta?: string;
}

const SIN_GUIA = "Cuando subas tu guía, aquí verás esta parte.";

// Estudiante independiente (puerta libre): de la guía al progreso.
export const RECORRIDO_ESTUDIANTE: PasoRecorrido[] = [
  {
    titulo: "Empieza con tu guía",
    texto: "Sube el PDF de tu curso o pega su texto. Todas las guías que subas quedan en «Mis guías».",
    destino: { name: RutaEnum.INICIO },
    ruta: RutaEnum.INICIO,
    objetivo: "guia-actual",
  },
  {
    titulo: "Tu PDF, tal como lo subiste",
    texto: "Si tu guía es un PDF, aquí lo ves completo para revisarlo mientras estudias.",
    destino: { name: RutaEnum.GUIA },
    ruta: RutaEnum.GUIA,
    objetivo: "documento",
    siFalta: "Cuando subas un PDF, aquí lo verás tal cual. Si pegaste texto, pasa a elegir un formato.",
  },
  {
    titulo: "Elige cómo aprenderlo",
    texto: "Mapa visual, ejemplo real, lectura fácil o audio. FROBI adapta el tema a tu manera de aprender.",
    destino: { name: RutaEnum.GUIA },
    ruta: RutaEnum.GUIA,
    objetivo: "formatos",
    siFalta: SIN_GUIA,
  },
  {
    titulo: "Así se lo pedí a la IA",
    texto:
      "Cada adaptación muestra su receta: contexto, objetivo, nivel y formato. Cópiala y úsala con cualquier IA.",
    destino: { name: RutaEnum.RESULTADO, params: { formato: "lectura-facil" } },
    ruta: RutaEnum.RESULTADO,
    objetivo: "receta",
    siFalta: SIN_GUIA,
  },
  {
    titulo: "Pide ayuda solo si la necesitas",
    texto:
      "La escalera te da pistas paso a paso. La respuesta final se abre después de tu intento, y resolver sin IA cuenta como logro.",
    destino: { name: RutaEnum.AYUDA, params: { tarea: TAREA_EJEMPLO } },
    ruta: RutaEnum.AYUDA,
    objetivo: "escalera",
    siFalta: SIN_GUIA,
  },
  {
    titulo: "Pídelo tú",
    texto: "Escribe tu propia instrucción a la IA. FROBI te dice qué pieza falta y cómo mejorarla.",
    destino: { name: RutaEnum.PIDELO_TU },
    ruta: RutaEnum.PIDELO_TU,
    objetivo: "instruccion",
  },
  {
    titulo: "Mira cómo vas",
    texto: "En «Mi progreso» ves en qué formato aprendes mejor, tus aciertos y lo que resolviste sin IA.",
    destino: { name: RutaEnum.PROGRESO },
    ruta: RutaEnum.PROGRESO,
    objetivo: "progreso",
    siFalta: "Cuando practiques, aquí aparecerá tu avance.",
  },
  {
    titulo: "Todo lo demás está en el menú",
    texto:
      "Trae tu trabajo para revisar tu borrador, herramientas recomendadas, ajustes y este recorrido, cuando quieras repetirlo.",
    objetivo: "menu",
  },
];

// Docente (puerta de clase): crear, invitar y ver el avance dentro de la clase.
export const RECORRIDO_DOCENTE: PasoRecorrido[] = [
  {
    titulo: "Crea tu clase",
    texto: "Ponle nombre y una primera tarea. FROBI genera un código para que tus alumnos se unan.",
    destino: { name: RutaEnum.CLASE_NUEVA },
    ruta: RutaEnum.CLASE_NUEVA,
    objetivo: "crear-clase",
  },
  {
    titulo: "Sube el contenido",
    texto: "Agrega los PDF de tu curso. Cada estudiante los podrá adaptar a su manera de aprender.",
    destino: { name: RutaEnum.CLASE_NUEVA },
    ruta: RutaEnum.CLASE_NUEVA,
    objetivo: "material-clase",
  },
  {
    titulo: "Invita a tus alumnos",
    texto:
      "Comparte el código o el enlace, o invítalos por su alias. No se piden correos ni datos personales.",
    destino: { name: RutaEnum.CLASE_INVITAR },
    ruta: RutaEnum.CLASE_INVITAR,
    objetivo: "codigo",
    siFalta: "Cuando crees tu clase, aquí verás su código.",
  },
  {
    titulo: "Sigue a cada alumno",
    texto:
      "Ves quién se unió, cómo va y dónde se traba. Abre su detalle para saber qué ayudas usó y qué proponerle.",
    destino: { name: RutaEnum.DOCENTE },
    ruta: RutaEnum.DOCENTE,
    objetivo: "mi-clase",
    siFalta: "Cuando tengas una clase, aquí verás a tus alumnos.",
  },
  {
    titulo: "Lo que pasa en tu clase",
    texto:
      "Formatos más pedidos, preguntas más falladas y uso de IA. Solo cuenta lo que ocurre dentro de tu clase.",
    destino: { name: RutaEnum.DOCENTE },
    ruta: RutaEnum.DOCENTE,
    objetivo: "estadisticas",
    siFalta: "Cuando tus alumnos practiquen, aquí verás el resumen de la clase.",
  },
  {
    titulo: "Todo lo demás está en el menú",
    texto: "También puedes estudiar tus propias guías, cambiar tus ajustes y repetir este recorrido.",
    objetivo: "menu",
  },
];
