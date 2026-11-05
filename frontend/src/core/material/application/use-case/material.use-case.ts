import { PdfIlegibleError, type MaterialPort } from "@/core/material/infraestructure/ports/in/material.port";
import type { ArchivoLeido, Material } from "@/core/shared/domain/view/material.view";
import { EstadoCargaEnum } from "@/core/shared/application/enum/estado-carga.enum";
import {
  escenarioSimulado,
  esperar,
  respuestaSimulada,
} from "@/core/shared/application/util/simulacion.util";
import { ARCHIVO_LEIDO_MOCK, MATERIAL_MOCK } from "@/mocks/material.mock";

const PASOS_SUBIDA = [15, 35, 60, 85, 100];

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class MaterialUseCase implements MaterialPort {
  obtenerGuia(_materialId: string): Promise<Material> {
    return respuestaSimulada(MATERIAL_MOCK);
  }

  async leerPdf(nombreArchivo: string, alAvanzar: (porcentaje: number) => void): Promise<ArchivoLeido> {
    for (const paso of PASOS_SUBIDA) {
      await esperar(350);
      alAvanzar(paso);
      // ?estado=error-respaldo simula un PDF escaneado que no se puede leer.
      if (paso >= 60 && escenarioSimulado() === EstadoCargaEnum.ERROR_RESPALDO) {
        throw new PdfIlegibleError();
      }
    }
    return respuestaSimulada({ ...ARCHIVO_LEIDO_MOCK, nombre: nombreArchivo }, 0);
  }
}
