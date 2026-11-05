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

// Panel docente: siempre datos de ejemplo en la maqueta.
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
  esEjemplo: true;
}
