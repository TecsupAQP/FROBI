import type { ArchivoLeido, Material } from "@/core/shared/domain/view/material.view";

export class PdfIlegibleError extends Error {
  constructor() {
    super("No pudimos leer este PDF");
    this.name = "PdfIlegibleError";
  }
}

export interface MaterialPort {
  obtenerGuia(materialId: string): Promise<Material>;
  // alAvanzar recibe 0–100 mientras se sube y se lee el archivo.
  leerPdf(nombreArchivo: string, alAvanzar: (porcentaje: number) => void): Promise<ArchivoLeido>;
}
