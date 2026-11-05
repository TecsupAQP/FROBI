import type { Adaptation, ContenidoAdaptado, FormatoId } from "@/core/shared/domain/view/adaptation.view";
import type { PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";

export const RECETA_MOCK: PiezaInstruccion[] = [
  { pieza: "contexto", texto: "Soy estudiante de primer ciclo de Mecatrónica." },
  { pieza: "objetivo", texto: "Necesito elegir un sensor para detectar botellas." },
  { pieza: "nivel", texto: "Explícalo sin fórmulas." },
  { pieza: "formato", texto: "Usa un ejemplo de una línea de embotellado." },
];

const CONTENIDOS_MOCK: Record<FormatoId, ContenidoAdaptado> = {
  "mapa-visual": {
    formato: "mapa-visual",
    conceptoCentral: "Sensor inductivo",
    nodos: [
      { titulo: "Campo electromagnético", detalle: "Lo genera la bobina del sensor" },
      { titulo: "Solo detecta metales", detalle: "No detecta vidrio ni plástico" },
      { titulo: "Sin contacto", detalle: "No se desgasta al detectar" },
      { titulo: "Cambia su señal", detalle: "Avisa a la máquina que hay un objeto" },
    ],
    usos: "Se usa para contar piezas, detectar tapas metálicas y controlar posiciones.",
  },
  "ejemplo-real": {
    formato: "ejemplo-real",
    pasos: [
      "La botella avanza por la faja.",
      "La tapa metálica entra en el campo del sensor.",
      "El sensor cambia su señal y la máquina cuenta 1 botella.",
    ],
    advertencia: "Ojo: el sensor inductivo detecta la tapa metálica, no el vidrio de la botella.",
  },
  "lectura-facil": {
    formato: "lectura-facil",
    frases: [
      "El sensor inductivo detecta metales.",
      "No necesita tocar el objeto.",
      "Crea un campo invisible.",
      "Si un metal entra en el campo, el sensor avisa.",
      "La máquina recibe ese aviso.",
      "Sirve para contar piezas y tapas.",
    ],
    glosario: [
      { termino: "Sensor", definicion: "Aparato que mide o detecta algo." },
      { termino: "Campo electromagnético", definicion: "Zona invisible alrededor del sensor." },
      { termino: "Señal de salida", definicion: "El aviso que el sensor manda a la máquina." },
      { termino: "Metálico", definicion: "Hecho de metal, como una tapa." },
    ],
  },
  audio: {
    formato: "audio",
    titulo: "Sensor inductivo · Audio",
    voz: "Voz en español",
    duracionSegundos: 130,
    posicionSegundos: 46,
    frases: [
      "El sensor inductivo detecta objetos metálicos sin tocarlos.",
      "Imagina una línea de embotellado: las botellas pasan por una faja.",
      "Cada botella lleva una tapa de metal. Cuando la tapa llega al sensor, el sensor avisa a la máquina.",
      "Así la máquina cuenta las botellas sin usar ninguna fórmula.",
    ],
    fraseActual: 1,
  },
};

export function adaptacionMock(formato: FormatoId, esRespaldo = false): Adaptation {
  return {
    materialId: "guia-sensores",
    temaId: "tema-1",
    ruta: ["Sensores industriales", "Tema 1"],
    titulo: "Sensor inductivo",
    receta: RECETA_MOCK,
    contenido: CONTENIDOS_MOCK[formato],
    esRespaldo,
  };
}
