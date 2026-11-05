import type { AyudaPort } from "@/core/ayuda/infraestructure/ports/in/ayuda.port";
import type { ResultadoIntento, TareaAyuda } from "@/core/shared/domain/view/ayuda.view";
import { respuestaSimulada } from "@/core/shared/application/util/simulacion.util";
import { CRITERIOS_SIN_IA_MOCK, TAREAS_AYUDA_MOCK } from "@/mocks/ayuda.mock";

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class AyudaUseCase implements AyudaPort {
  obtenerTarea(tareaId: string): Promise<TareaAyuda | null> {
    return respuestaSimulada(TAREAS_AYUDA_MOCK[tareaId] ?? null, 400);
  }

  probarIntento(_tareaId: string, intento: string): Promise<ResultadoIntento> {
    const correcto = /capacitiv|óptic|optic/i.test(intento);
    return respuestaSimulada(
      {
        correcto,
        comentario: correcto
          ? "Vas bien: ese sensor sí detecta vidrio. Compara tu explicación con la respuesta final."
          : "Todavía no. Ya puedes abrir la respuesta final o pedir el paso a paso.",
      },
      800,
    );
  }

  obtenerCriteriosSinIa(_tareaId: string): Promise<string[]> {
    return respuestaSimulada(CRITERIOS_SIN_IA_MOCK, 300);
  }
}
