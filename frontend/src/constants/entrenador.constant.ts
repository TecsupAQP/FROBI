import type { Autonomia } from "@/core/shared/domain/view/prompt-score.view";
import type { NivelAutonomia, PiezaId, PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";

const NOMBRES_NIVEL: Record<NivelAutonomia, string> = { 1: "Con plantilla", 2: "Con pistas", 3: "Sin ayuda" };

// Plantilla para el nivel 1 de autonomía: la persona completa los espacios.
export const PLANTILLA_INSTRUCCION: PiezaInstruccion[] = [
  { pieza: "contexto", texto: "Soy estudiante de [ciclo] de [carrera]." },
  { pieza: "objetivo", texto: "Necesito [lo que quieres lograr]." },
  { pieza: "nivel", texto: "Explícalo [sin fórmulas, con detalle…]." },
  { pieza: "formato", texto: "Usa [un ejemplo, un mapa…]." },
];

// Conteo rápido mientras se escribe, sin llamar a la API. La evaluación real la hace el backend.
const PATRONES: Record<PiezaId, RegExp> = {
  contexto: /\b(soy|estudio|estudiante|ciclo|carrera)\b/i,
  objetivo: /\b(necesito|quiero|para|objetivo|lograr|elegir)\b/i,
  nivel: /\b(sin f[oó]rmulas|simple|sencill|detalle|b[aá]sico|profund|nivel|conocimientos)/i,
  formato: /\b(expl[ií]ca|ejemplo|mapa|lista|resumen|tabla|audio|paso a paso|puntos|resp[oó]ndeme)/i,
};

export const ORDEN_PIEZAS: PiezaId[] = ["contexto", "objetivo", "nivel", "formato"];

export function piezasDetectadas(instruccion: string): PiezaId[] {
  return ORDEN_PIEZAS.filter((pieza) => PATRONES[pieza].test(instruccion));
}

export function construirAutonomia(nivel: number, mensaje: string): Autonomia {
  const nivelActual = Math.min(3, Math.max(1, Math.round(nivel))) as NivelAutonomia;
  const niveles = ([1, 2, 3] as const).map((item) => ({
    nivel: item,
    nombre: NOMBRES_NIVEL[item],
    estado:
      item < nivelActual
        ? ("superado" as const)
        : item === nivelActual
          ? ("actual" as const)
          : ("bloqueado" as const),
  }));
  return { nivelActual, niveles, mensaje };
}
