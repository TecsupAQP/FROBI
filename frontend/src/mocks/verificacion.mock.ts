import type { Verificacion } from "@/core/shared/domain/view/pregunta.view";

export const VERIFICACION_MOCK: Verificacion = {
  ruta: ["Sensores industriales", "Tema 1", "Verificación"],
  preguntas: [
    {
      id: "p1",
      enunciado: "¿Qué detecta un sensor inductivo?",
      opciones: [
        { id: "a", letra: "A", texto: "Objetos metálicos" },
        { id: "b", letra: "B", texto: "Cualquier objeto transparente" },
        { id: "c", letra: "C", texto: "Solo líquidos" },
      ],
      correcta: "a",
      explicacionAcierto: "Un sensor inductivo detecta objetos metálicos, como la tapa de la botella.",
      explicacionError:
        "El sensor inductivo solo detecta metales, no vidrio ni plástico. En la botella, detecta la tapa.",
      formatoSugerido: "lectura-facil",
    },
    {
      id: "p2",
      enunciado: "¿Necesita tocar el objeto para detectarlo?",
      opciones: [
        { id: "a", letra: "A", texto: "Sí, debe tocarlo" },
        { id: "b", letra: "B", texto: "No, lo detecta sin contacto" },
        { id: "c", letra: "C", texto: "Solo si el objeto es grande" },
      ],
      correcta: "b",
      explicacionAcierto: "Detecta sin contacto, por eso no se desgasta.",
      explicacionError: "Funciona sin contacto: el metal solo tiene que entrar en su campo.",
      formatoSugerido: "mapa-visual",
    },
    {
      id: "p3",
      enunciado: "En una línea de embotellado, ¿qué parte de la botella detecta?",
      opciones: [
        { id: "a", letra: "A", texto: "El vidrio de la botella" },
        { id: "b", letra: "B", texto: "El líquido de adentro" },
        { id: "c", letra: "C", texto: "La tapa metálica" },
      ],
      correcta: "c",
      explicacionAcierto: "Exacto: detecta la tapa metálica, no el vidrio.",
      explicacionError: "El vidrio no es metálico; lo que detecta es la tapa.",
      formatoSugerido: "ejemplo-real",
    },
  ],
};
