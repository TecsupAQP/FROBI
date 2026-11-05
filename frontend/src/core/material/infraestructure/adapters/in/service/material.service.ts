import type { MaterialPort } from "@/core/material/infraestructure/ports/in/material.port";
import { MaterialUseCase } from "@/core/material/application/use-case/material.use-case";

const materialPort: MaterialPort = new MaterialUseCase();

export const obtenerGuiaService = () => materialPort.obtenerGuia();
export const listarGuiasService = () => materialPort.listarGuias();
export const leerPdfService = (archivo: File, alAvanzar: (porcentaje: number) => void) =>
  materialPort.leerPdf(archivo, alAvanzar);
export const pegarTextoService = (titulo: string, texto: string) => materialPort.pegarTexto(titulo, texto);
export const usarMaterialService = (materialId: string) => materialPort.usarMaterial(materialId);
