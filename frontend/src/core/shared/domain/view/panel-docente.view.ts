export interface DatoPorcentaje {
  etiqueta: string;
  porcentaje: number;
}

export interface DatoConteo {
  etiqueta: string;
  valor: number;
  total: number;
}

export interface GrupoDocente {
  id: string;
  nombre: string;
  estudiantes: number;
}

export interface DetalleEstudiante {
  alias: string;
  formatoPreferido: string;
  aciertos: number;
  puntajeInstrucciones: string;
  autonomia: string;
  preguntaMasFallada: string;
}

// Panel docente de una clase. esEjemplo: la API todavía muestra datos de ejemplo.
export interface PanelDocente {
  grupo: GrupoDocente;
  grupos: GrupoDocente[];
  formatosPedidos: DatoPorcentaje[];
  preguntasFalladas: DatoPorcentaje[];
  temasDificiles: DatoPorcentaje[];
  sugerencia: string;
  actividadesPromedio: number;
  usoIa: DatoConteo[];
  competencias: DatoPorcentaje[];
  estudiantes: DetalleEstudiante[];
  esEjemplo: boolean;
}
