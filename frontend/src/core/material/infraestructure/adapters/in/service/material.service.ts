import type { MaterialPort } from "@/core/material/infraestructure/ports/in/material.port";
import { MaterialUseCase } from "@/core/material/application/use-case/material.use-case";

const materialPort: MaterialPort = new MaterialUseCase();

export const obtenerGuiaService = (materialId: string) => materialPort.obtenerGuia(materialId);
export const leerPdfService = (nombreArchivo: string, alAvanzar: (porcentaje: number) => void) =>
  materialPort.leerPdf(nombreArchivo, alAvanzar);
