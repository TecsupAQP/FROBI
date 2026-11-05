import type { DocentePort } from "@/core/docente/infraestructure/ports/in/docente.port";
import type { DatoPorcentaje, PanelDocente } from "@/core/shared/domain/view/panel-docente.view";
import { api } from "@/core/shared/infraestructure/http/api.client";
import type { ClaseDto, PanelDto } from "@/core/shared/infraestructure/http/api.dto";
import { formatoDesdeApi, nombreFormato } from "@/core/shared/infraestructure/http/api.mapper";
import { claseActualId } from "@/core/shared/infraestructure/http/clase-actual";

const porcentaje = (valor: number, total: number) => (total ? Math.round((valor / total) * 100) : 0);

// GET /classes/{id} y /classes/{id}/dashboard. Solo cuenta la actividad dentro de la clase.
export class DocenteUseCase implements DocentePort {
  async obtenerPanel(): Promise<PanelDocente | null> {
    const id = await claseActualId();
    if (!id) return null;
    const [clase, panel] = await Promise.all([
      api.get<ClaseDto>(`/classes/${id}`),
      api.get<PanelDto>(`/classes/${id}/dashboard`),
    ]);

    const totalFormatos = panel.top_formats.reduce((suma, dato) => suma + dato.count, 0);
    const formatosPedidos: DatoPorcentaje[] = panel.top_formats.map((dato) => ({
      etiqueta: nombreFormato(formatoDesdeApi(dato.format)),
      porcentaje: porcentaje(dato.count, totalFormatos),
    }));
    const preguntasFalladas: DatoPorcentaje[] = panel.most_failed_questions.map((pregunta) => ({
      etiqueta: pregunta.statement,
      porcentaje: Math.round(pregunta.fail_rate * 100),
    }));
    const { help_requests: ayudas, solved_without_ai: sinIa } = panel.ai_usage;
    const totalActividades = ayudas + sinIa;
    const alumnos = panel.students.length;
    const trabados = panel.students.flatMap((alumno) => alumno.alerts);

    const grupo = { id: clase.id, nombre: clase.name, estudiantes: alumnos };
    return {
      grupo,
      grupos: [grupo],
      formatosPedidos,
      preguntasFalladas,
      // La API agrupa las trabas por alumno: se muestran como "dónde se traban".
      temasDificiles: [...new Set(trabados.map((alerta) => alerta.text))].map((texto) => ({
        etiqueta: texto,
        porcentaje: porcentaje(trabados.filter((alerta) => alerta.text === texto).length, alumnos),
      })),
      sugerencia: preguntasFalladas[0]
        ? `Repasa en clase «${preguntasFalladas[0].etiqueta}» con un ejemplo real.`
        : "Tu clase va bien. Propón un ejercicio para resolver sin IA.",
      actividadesPromedio: alumnos ? Math.round((totalActividades / alumnos) * 10) / 10 : 0,
      usoIa: [
        { etiqueta: "Pidieron ayuda a la escalera", valor: ayudas, total: totalActividades },
        { etiqueta: "Resolvieron sin IA", valor: sinIa, total: totalActividades },
      ],
      // La API todavía no mide competencias en IA por clase.
      competencias: [],
      estudiantes: [],
      esEjemplo: panel.sample_data,
    };
  }
}
