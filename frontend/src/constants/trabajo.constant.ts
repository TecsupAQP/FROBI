import type { BorradorTrabajo } from "@/core/shared/domain/view/claim-review.view";

// Ejemplo con el que arranca "Trae tu trabajo" para mostrar la revisión de afirmaciones.
export const BORRADOR_EJEMPLO: BorradorTrabajo = {
  consigna:
    "Informe de 1 página: elige un sensor para detectar botellas en una línea de embotellado y justifica tu elección.",
  borrador:
    "El sensor inductivo detecta botellas de vidrio sin tocarlas. Se usa mucho en líneas de embotellado porque es rápido. El sensor óptico suele ser más caro, por eso recomiendo el inductivo.",
};
