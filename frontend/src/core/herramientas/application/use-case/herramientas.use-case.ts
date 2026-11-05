import type {
  AfirmacionRevisada,
  HerramientasPort,
} from "@/core/herramientas/infraestructure/ports/in/herramientas.port";
import type { IconoHerramienta, RecomendacionHerramientas, Tool } from "@/core/shared/domain/view/tool.view";
import { api } from "@/core/shared/infraestructure/http/api.client";
import type { HerramientaDto, RecomendacionDto } from "@/core/shared/infraestructure/http/api.dto";

// Nombre e ícono de cada necesidad del catálogo de la API.
const NECESIDADES: Record<string, { nombre: string; icono: IconoHerramienta }> = {
  verify_source: { nombre: "Verificar un dato", icono: "search" },
  study_material: { nombre: "Estudiar tu material", icono: "book" },
  calculate: { nombre: "Calcular", icono: "spark" },
  write: { nombre: "Escribir", icono: "file" },
  visualize: { nombre: "Ordenar ideas", icono: "org" },
};

const necesidad = (id: string) => NECESIDADES[id] ?? { nombre: id, icono: "spark" as IconoHerramienta };

const herramientaDesdeApi = (dto: HerramientaDto, recomendacion?: RecomendacionDto): Tool => ({
  id: dto.id,
  nombre: dto.name,
  icono: necesidad(dto.need).icono,
  paraQue: necesidad(dto.need).nombre,
  necesidades: [dto.need],
  usala: dto.use_for,
  noLaUses: dto.avoid_for,
  porQueSirve: recomendacion?.why ?? dto.use_for,
  cuandoNoUsarla: recomendacion?.when_not ?? dto.avoid_for,
});

// GET /tools (catálogo fijo de 5) y POST /tools/recommendations.
export class HerramientasUseCase implements HerramientasPort {
  async obtenerRecomendacion(afirmacion: AfirmacionRevisada | null): Promise<RecomendacionHerramientas> {
    const [catalogo, recomendacion] = await Promise.all([
      api.get<HerramientaDto[]>("/tools"),
      api.post<RecomendacionDto>(
        "/tools/recommendations",
        afirmacion ? { claim_id: afirmacion.id } : { need: "verify_source" },
      ),
    ]);
    const necesidades = [...new Set(catalogo.map((herramienta) => herramienta.need))];
    return {
      afirmacion: afirmacion?.texto ?? "",
      necesidadSugerida: recomendacion.tool.need,
      necesidades: necesidades.map((id) => ({ id, nombre: necesidad(id).nombre })),
      // La recomendada va primero, con el porqué que da la API.
      catalogo: [
        herramientaDesdeApi(recomendacion.tool, recomendacion),
        ...catalogo
          .filter((item) => item.id !== recomendacion.tool.id)
          .map((item) => herramientaDesdeApi(item)),
      ],
    };
  }
}
