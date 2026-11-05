export type NecesidadId = "buscar-fuentes" | "verificar-dato" | "estructurar" | "explicar" | "practicar";

// Iconos disponibles para herramientas (deben existir en el registro de iconos).
export type IconoHerramienta = "file" | "search" | "book" | "spark" | "org";

export interface Necesidad {
  id: NecesidadId;
  nombre: string;
}

export interface Tool {
  id: string;
  nombre: string;
  icono: IconoHerramienta;
  // Texto corto bajo el nombre: "Buscar fuentes", "Explicar o practicar"…
  paraQue: string;
  necesidades: NecesidadId[];
  usala: string;
  noLaUses: string;
  porQueSirve: string;
  cuandoNoUsarla: string;
}

export interface RecomendacionHerramientas {
  afirmacion: string;
  necesidades: Necesidad[];
  catalogo: Tool[];
}
