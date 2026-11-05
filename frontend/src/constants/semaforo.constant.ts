import type { EstadoAfirmacion } from "@/core/shared/domain/view/claim-review.view";
import type { NombreIcono } from "@/constants/iconos.constant";

export interface DefinicionSemaforo {
  texto: string;
  // Para el resumen: "1 con respaldo", "2 no se pueden comprobar"…
  textoConteo: (cantidad: number) => string;
  icono: NombreIcono;
}

// Icono + texto + color: el estado nunca depende solo del color.
export const SEMAFORO: Record<EstadoAfirmacion, DefinicionSemaforo> = {
  "con-respaldo": {
    texto: "Con respaldo",
    textoConteo: (cantidad) => `${cantidad} con respaldo`,
    icono: "check",
  },
  "no-comprobable": {
    texto: "No se puede comprobar",
    textoConteo: (cantidad) =>
      cantidad === 1 ? "1 no se puede comprobar" : `${cantidad} no se pueden comprobar`,
    icono: "warn",
  },
  contradice: {
    texto: "Contradice tu material",
    textoConteo: (cantidad) =>
      cantidad === 1 ? "1 contradice tu material" : `${cantidad} contradicen tu material`,
    icono: "xc",
  },
};
