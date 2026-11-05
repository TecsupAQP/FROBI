import type { TrabajoPort } from "@/core/trabajo/infraestructure/ports/in/trabajo.port";
import type {
  BorradorTrabajo,
  EstadoAfirmacion,
  WorkReview,
} from "@/core/shared/domain/view/claim-review.view";
import { api } from "@/core/shared/infraestructure/http/api.client";
import type {
  EstadoAfirmacionApi,
  MaterialDto,
  RevisionDto,
  TrabajoDto,
} from "@/core/shared/infraestructure/http/api.dto";

// Nunca se dice "falso": los tres estados posibles de una afirmación.
const ESTADOS: Record<EstadoAfirmacionApi, EstadoAfirmacion> = {
  supported: "con-respaldo",
  unverifiable: "no-comprobable",
  contradicts: "contradice",
};

// POST /materials (consigna y borrador), POST /works y POST /works/{id}/claim-review.
export class TrabajoUseCase implements TrabajoPort {
  async revisarTrabajo(trabajo: BorradorTrabajo): Promise<WorkReview> {
    const [consigna, borrador] = await Promise.all([
      api.post<MaterialDto>("/materials", { title: "Consigna", kind: "brief", text: trabajo.consigna }),
      api.post<MaterialDto>("/materials", { title: "Borrador", kind: "draft", text: trabajo.borrador }),
    ]);
    const creado = await api.post<TrabajoDto>("/works", {
      brief_material_id: consigna.id,
      draft_material_id: borrador.id,
    });
    const revision = await api.post<RevisionDto>(`/works/${creado.id}/claim-review`);

    const resumen: Record<EstadoAfirmacion, number> = {
      "con-respaldo": 0,
      "no-comprobable": 0,
      contradice: 0,
    };
    const secciones = revision.sections.map((seccion, indice) => ({
      id: `seccion-${indice + 1}`,
      numero: indice + 1,
      titulo: seccion.section,
      afirmaciones: seccion.claims.map((afirmacion) => {
        const estado = ESTADOS[afirmacion.status];
        resumen[estado] += 1;
        return {
          id: afirmacion.id,
          texto: afirmacion.fragment,
          estado,
          citaGuia: afirmacion.backing_passage ?? undefined,
          motivo: afirmacion.no_backing_message ?? afirmacion.reason,
        };
      }),
    }));
    return { id: creado.id, consigna: trabajo.consigna, secciones, resumen };
  }
}
