import type { ArchivoLeido, Material } from "@/core/shared/domain/view/material.view";

export const MATERIAL_MOCK: Material = {
  id: "guia-sensores",
  titulo: "Sensores industriales",
  carrera: "Mecatrónica",
  descripcion:
    "Aprende cómo detectan objetos los sensores inductivos, capacitivos y ópticos, y cómo elegir el correcto para una línea de producción.",
  etiquetas: ["Inductivos", "Capacitivos", "Ópticos"],
  minutosLectura: 12,
  temas: [
    {
      id: "tema-1",
      numero: 1,
      titulo: "Sensor inductivo",
      textoOriginal:
        "Un sensor inductivo detecta objetos metálicos sin tocarlos. Genera un campo electromagnético y, cuando un metal entra en ese campo, cambia su señal de salida. Se usa para contar piezas de metal, detectar tapas metálicas y controlar posiciones en las máquinas.",
    },
    {
      id: "tema-2",
      numero: 2,
      titulo: "Sensor capacitivo",
      textoOriginal:
        "Un sensor capacitivo detecta metales, plásticos y líquidos por el cambio en su campo eléctrico. Sirve para medir el nivel de un tanque o detectar envases de plástico.",
    },
    {
      id: "tema-3",
      numero: 3,
      titulo: "Sensor óptico",
      textoOriginal:
        "Un sensor óptico usa un haz de luz y detecta un objeto cuando lo interrumpe o lo refleja. Funciona con vidrio, plástico y cartón, por eso se usa para contar botellas en una faja.",
    },
  ],
};

export const ARCHIVO_LEIDO_MOCK: ArchivoLeido = {
  nombre: "guia-sensores.pdf",
  paginas: 4,
  tamanoMb: 2.4,
  vistaPrevia: {
    titulo: "Sensores industriales",
    texto:
      "Un sensor inductivo detecta objetos metálicos sin tocarlos. Genera un campo electromagnético y, cuando un metal entra en él, cambia su señal de salida. Un sensor capacitivo detecta metales, plásticos y líquidos por el cambio en su campo eléctrico. Un sensor óptico usa un haz de luz y detecta un objeto cuando lo interrumpe o lo refleja.",
  },
};
