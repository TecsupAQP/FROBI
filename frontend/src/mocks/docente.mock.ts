import type { DetalleEstudiante, PanelDocente } from "@/core/shared/domain/view/panel-docente.view";

const ESTUDIANTES: DetalleEstudiante[] = [
  {
    alias: "estudiante_07",
    formatoPreferido: "Ejemplo real",
    aciertos: 80,
    puntajeInstrucciones: "de 2/4 a 4/4 piezas",
    autonomia: "Nivel 2 · Con pistas",
    preguntaMasFallada: "¿Qué detecta un sensor inductivo?",
  },
  {
    alias: "estudiante_12",
    formatoPreferido: "Mapa visual",
    aciertos: 65,
    puntajeInstrucciones: "de 1/4 a 3/4 piezas",
    autonomia: "Nivel 1 · Con plantilla",
    preguntaMasFallada: "¿Cuándo conviene un sensor óptico?",
  },
  {
    alias: "estudiante_19",
    formatoPreferido: "Lectura fácil",
    aciertos: 90,
    puntajeInstrucciones: "de 3/4 a 4/4 piezas",
    autonomia: "Nivel 3 · Sin ayuda",
    preguntaMasFallada: "¿Qué es un campo electromagnético?",
  },
];

export const PANEL_DOCENTE_MOCK: PanelDocente = {
  grupo: { id: "meca-1", nombre: "Mecatrónica · 1.º ciclo", estudiantes: 24 },
  grupos: [
    { id: "meca-1", nombre: "Mecatrónica · 1.º ciclo", estudiantes: 24 },
    { id: "meca-3", nombre: "Mecatrónica · 3.er ciclo", estudiantes: 19 },
    { id: "elec-1", nombre: "Electrónica · 1.º ciclo", estudiantes: 27 },
  ],
  formatosPedidos: [
    { etiqueta: "Ejemplo real", porcentaje: 42 },
    { etiqueta: "Mapa visual", porcentaje: 28 },
    { etiqueta: "Lectura fácil", porcentaje: 18 },
    { etiqueta: "Audio", porcentaje: 12 },
  ],
  preguntasFalladas: [
    { etiqueta: "¿Qué detecta un sensor inductivo?", porcentaje: 46 },
    { etiqueta: "¿Cuándo conviene un sensor óptico?", porcentaje: 38 },
    { etiqueta: "¿Qué es un campo electromagnético?", porcentaje: 31 },
  ],
  temasDificiles: [
    { etiqueta: "2. Sensor capacitivo", porcentaje: 52 },
    { etiqueta: "3. Sensor óptico", porcentaje: 35 },
    { etiqueta: "1. Sensor inductivo", porcentaje: 20 },
  ],
  sugerencia: "Refuerza el tema 2 con Lectura fácil.",
  actividadesPromedio: 3.2,
  usoIa: [
    { etiqueta: "Declararon herramientas externas", valor: 12, total: 24 },
    { etiqueta: "Completaron la verificación", valor: 19, total: 24 },
  ],
  competencias: [
    { etiqueta: "Formular instrucciones", porcentaje: 62 },
    { etiqueta: "Verificar información", porcentaje: 48 },
    { etiqueta: "Reconocer límites de la IA", porcentaje: 55 },
  ],
  estudiantes: ESTUDIANTES,
  esEjemplo: true,
};
