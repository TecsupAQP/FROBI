import type { EntrenadorPort } from "@/core/entrenador/infraestructure/ports/in/entrenador.port";
import type {
  Autonomia,
  InstruccionMejorada,
  PromptScore,
} from "@/core/shared/domain/view/prompt-score.view";
import type { PiezaId, PiezaInstruccion } from "@/core/shared/domain/view/pieza.view";
import { respuestaSimulada } from "@/core/shared/application/util/simulacion.util";
import {
  INSTRUCCION_MEJORADA_MOCK,
  PLANTILLA_MOCK,
  autonomiaMock,
  evaluacionMock,
  piezasDetectadas,
} from "@/mocks/entrenador.mock";

// Implementación mock. Para conectar el backend, reemplazar solo este archivo.
export class EntrenadorUseCase implements EntrenadorPort {
  obtenerAutonomia(): Promise<Autonomia> {
    return respuestaSimulada(autonomiaMock(1, "Con plantilla: completa los espacios de cada pieza."));
  }

  obtenerPlantilla(): Promise<PiezaInstruccion[]> {
    return respuestaSimulada(PLANTILLA_MOCK, 150);
  }

  evaluarInstruccion(instruccion: string): Promise<PromptScore> {
    return respuestaSimulada(evaluacionMock(instruccion), 1200);
  }

  mejorarInstruccion(_instruccion: string): Promise<InstruccionMejorada> {
    return respuestaSimulada(INSTRUCCION_MEJORADA_MOCK, 1200);
  }

  contarPiezas(instruccion: string): PiezaId[] {
    return piezasDetectadas(instruccion);
  }
}
