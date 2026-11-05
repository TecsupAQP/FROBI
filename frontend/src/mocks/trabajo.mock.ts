import type { BorradorTrabajo, WorkReview } from "@/core/shared/domain/view/claim-review.view";

export const BORRADOR_MOCK: BorradorTrabajo = {
  consigna:
    "Informe de 1 página: elige un sensor para detectar botellas en una línea de embotellado y justifica tu elección.",
  borrador:
    "El sensor inductivo detecta botellas de vidrio sin tocarlas. Se usa mucho en líneas de embotellado porque es rápido. El sensor óptico suele ser más caro, por eso recomiendo el inductivo.",
};

export const REVISION_MOCK: WorkReview = {
  consigna: BORRADOR_MOCK.consigna,
  secciones: [
    {
      id: "introduccion",
      numero: 1,
      titulo: "Introducción",
      texto: "Las líneas de embotellado necesitan detectar cada botella para contarla.",
      afirmaciones: [],
      estadoSeccion: { estado: "con-respaldo", texto: "Con respaldo" },
    },
    {
      id: "seleccion",
      numero: 2,
      titulo: "Selección del sensor",
      afirmaciones: [
        {
          id: "af-vidrio",
          texto: "El sensor inductivo detecta botellas de vidrio sin tocarlas.",
          estado: "contradice",
          citaGuia: "Un sensor inductivo detecta objetos metálicos sin tocarlos.",
          motivo: "Por qué conviene revisarlo: el vidrio no es metálico.",
        },
        {
          id: "af-rapido",
          texto: "Se usa mucho en líneas de embotellado porque es rápido.",
          estado: "no-comprobable",
          motivo: "No aparece en tu material. Pide una fuente antes de afirmarlo.",
        },
      ],
    },
    {
      id: "conclusion",
      numero: 3,
      titulo: "Conclusión",
      texto: "Por eso recomiendo el inductivo.",
      afirmaciones: [],
      estadoSeccion: { estado: "con-respaldo", texto: "Sin afirmaciones por revisar" },
    },
  ],
  resumen: { "con-respaldo": 1, "no-comprobable": 1, contradice: 1 },
};
