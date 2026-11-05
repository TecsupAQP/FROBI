import type {
  Autonomia,
  InstruccionMejorada,
  PromptScore,
} from "@/core/shared/domain/view/prompt-score.view";
import type { NivelAutonomia, PiezaId, PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";
import { RECETA_MOCK } from "@/mocks/adaptacion.mock";

export const TEMA_ENTRENADOR = "Sensor inductivo";

const NOMBRES_NIVEL: Record<NivelAutonomia, string> = { 1: "Con plantilla", 2: "Con pistas", 3: "Sin ayuda" };

export const PLANTILLA_MOCK: PiezaInstruccion[] = [
  { pieza: "contexto", texto: "Soy estudiante de [ciclo] de [carrera]." },
  { pieza: "objetivo", texto: "Necesito [lo que quieres lograr]." },
  { pieza: "nivel", texto: "Explícalo [sin fórmulas, con detalle…]." },
  { pieza: "formato", texto: "Usa [un ejemplo, un mapa…]." },
];

// Detección simulada por palabras clave; el backend real hará esta evaluación.
const PATRONES: Record<PiezaId, RegExp> = {
  contexto: /\b(soy|estudio|estudiante|ciclo|carrera)\b/i,
  objetivo: /\b(necesito|quiero|para|objetivo|lograr|elegir)\b/i,
  nivel: /\b(sin f[oó]rmulas|simple|sencill|detalle|b[aá]sico|profund|nivel)/i,
  formato: /\b(expl[ií]ca|ejemplo|mapa|lista|resumen|tabla|audio|paso a paso)/i,
};

const FALTA: Record<PiezaId, string> = {
  contexto: "Falta: ¿quién eres y qué estudias?",
  objetivo: "Falta: ¿para qué lo necesitas?",
  nivel: "Falta: ¿con cuánta profundidad?",
  formato: "Falta: ¿cómo lo quieres recibir?",
};

const PRESENTE: Record<PiezaId, string> = {
  contexto: "Dices quién eres.",
  objetivo: "Dices para qué lo necesitas.",
  nivel: "Indicas la profundidad.",
  formato: "Pides una explicación.",
};

const ORDEN: PiezaId[] = ["contexto", "objetivo", "nivel", "formato"];

export function piezasDetectadas(instruccion: string): PiezaId[] {
  return ORDEN.filter((pieza) => PATRONES[pieza].test(instruccion));
}

export function evaluacionMock(instruccion: string): PromptScore {
  const detectadas = piezasDetectadas(instruccion);
  const piezas = ORDEN.map((pieza) => {
    const presente = detectadas.includes(pieza);
    return { pieza, presente, comentario: presente ? PRESENTE[pieza] : FALTA[pieza] };
  });
  return {
    instruccion,
    piezas,
    presentes: detectadas.length,
    total: ORDEN.length,
    sugerencia:
      detectadas.length < ORDEN.length
        ? {
            texto: "Añade quién eres y para qué lo necesitas.",
            ejemplo:
              "Soy estudiante de primer ciclo de Mecatrónica. Necesito elegir un sensor para detectar botellas.",
          }
        : null,
    autonomia: autonomiaMock(2, "Aquí te damos pistas por pieza, sin escribir por ti."),
  };
}

export const INSTRUCCION_MEJORADA_MOCK: InstruccionMejorada = {
  receta: RECETA_MOCK,
  resultado: [
    "Para detectar botellas en una línea de embotellado conviene un sensor óptico, porque ve el vidrio y el plástico. El sensor inductivo solo sirve si quieres detectar la tapa metálica.",
    "Ejemplo: la faja avanza, el sensor óptico ve pasar la botella y la máquina la cuenta.",
  ],
  autonomia: autonomiaMock(2, "Un intento más sin ayuda y pasas al nivel 3."),
};

export function autonomiaMock(nivelActual: NivelAutonomia, mensaje: string): Autonomia {
  const niveles = ([1, 2, 3] as const).map((nivel) => ({
    nivel,
    nombre: NOMBRES_NIVEL[nivel],
    estado:
      nivel < nivelActual
        ? ("superado" as const)
        : nivel === nivelActual
          ? ("actual" as const)
          : ("bloqueado" as const),
  }));
  return { nivelActual, niveles, mensaje };
}
