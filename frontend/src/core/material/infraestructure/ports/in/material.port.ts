import type { ArchivoLeido, Material } from "@/core/shared/domain/view/material.view";

export class PdfIlegibleError extends Error {
  constructor() {
    super("No pudimos leer este PDF");
    this.name = "PdfIlegibleError";
  }
}

export interface MaterialPort {
  // La guía que estudia la persona: la de ejemplo o la que subió.
  obtenerGuia(): Promise<Material>;
  // alAvanzar recibe 0–100 mientras se sube y se lee el archivo.
  leerPdf(archivo: File, alAvanzar: (porcentaje: number) => void): Promise<ArchivoLeido>;
  // Cuando el PDF no se puede leer, la persona pega el texto.
  pegarTexto(titulo: string, texto: string): Promise<string>;
  // Desde aquí, la guía, las adaptaciones y la escalera usan este material.
  usarMaterial(materialId: string): void;
}
