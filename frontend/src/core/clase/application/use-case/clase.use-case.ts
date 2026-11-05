import type { ClasePort } from "@/core/clase/infraestructure/ports/in/clase.port";
import type {
  AlumnoClase,
  Clase,
  DetalleAlumno,
  EstadoAlumno,
  NuevaClase,
} from "@/core/shared/domain/view/clase.view";
import { api } from "@/core/shared/infraestructure/http/api.client";
import type {
  ClaseDto,
  DetalleEstudianteDto,
  EscalonApi,
  MiembroDto,
  MiembrosDto,
  PanelDto,
  YoDto,
} from "@/core/shared/infraestructure/http/api.dto";
import { formatoDesdeApi, nombreFormato } from "@/core/shared/infraestructure/http/api.mapper";
import { claseActualId, guardarClaseId, leerClaseId } from "@/core/shared/infraestructure/http/clase-actual";

const ESTADOS: Record<MiembroDto["status"], EstadoAlumno> = {
  invited: "invitado",
  joined: "se-unio",
  left: "salio",
};

const NOMBRE_ESCALON: Record<EscalonApi, string> = {
  hint_1: "Pista 1",
  hint_2: "Pista 2",
  step_by_step: "Paso a paso",
  final: "Respuesta final",
};

function alumnoDesdeApi(miembro: MiembroDto, panel: PanelDto | null): AlumnoClase {
  const fila = panel?.students.find(
    (alumno) => alumno.person_id === miembro.person_id || alumno.alias === miembro.alias,
  );
  const traba = fila?.alerts[0];
  return {
    personaId: miembro.person_id,
    alias: miembro.alias.toLowerCase(),
    nombre: miembro.alias,
    estado: ESTADOS[miembro.status],
    avance: null,
    posicion: miembro.status_label,
    // El avance en palabras, si no es lo mismo que ya dice la alerta.
    nota: fila && fila.progress_label !== (traba?.text ?? "Va bien") ? fila.progress_label : "",
    alerta: traba
      ? { tipo: "se-traba", texto: traba.text }
      : fila?.progress_label === "Va bien"
        ? { tipo: "va-bien", texto: "Va bien" }
        : null,
  };
}

function claseDesdeApi(clase: ClaseDto, miembros: MiembrosDto | null, panel: PanelDto | null): Clase {
  const [carrera = clase.subject, ciclo = ""] = clase.subject.split("·").map((parte) => parte.trim());
  return {
    id: clase.id,
    nombre: clase.name,
    carrera,
    ciclo,
    codigo: miembros?.invite_code ?? clase.invite_code,
    alumnos: (miembros?.members ?? []).map((miembro) => alumnoDesdeApi(miembro, panel)),
    esEjemplo: panel?.sample_data ?? false,
  };
}

// POST /classes, GET /classes/{id}, /members, /dashboard, /students/{person_id},
// POST /classes/{id}/invitations y /materials, DELETE /me/membership.
export class ClaseUseCase implements ClasePort {
  async obtenerClase(): Promise<Clase | null> {
    const yo = await api.get<YoDto>("/me");
    if (yo.person.role !== "teacher") {
      // El estudiante solo ve el nombre de su clase; el detalle es del docente.
      if (!yo.membership) return null;
      return {
        id: yo.membership.class_id,
        nombre: yo.membership.class_name,
        carrera: "",
        ciclo: "",
        codigo: "",
        alumnos: [],
        esEjemplo: false,
      };
    }
    const id = await claseActualId(yo);
    if (!id) return null;
    const [clase, miembros, panel] = await Promise.all([
      api.get<ClaseDto>(`/classes/${id}`),
      api.get<MiembrosDto>(`/classes/${id}/members`),
      api.get<PanelDto>(`/classes/${id}/dashboard`),
    ]);
    return claseDesdeApi(clase, miembros, panel);
  }

  async crearClase(datos: NuevaClase): Promise<Clase> {
    const clase = await api.post<ClaseDto>("/classes", {
      name: datos.nombre,
      subject: [datos.carrera, datos.ciclo].filter(Boolean).join(" · "),
      tasks: datos.tareas.filter((tarea) => tarea.trim()),
    });
    guardarClaseId(clase.id);
    for (const archivo of datos.archivos) {
      const formulario = new FormData();
      formulario.append("title", archivo.name.replace(/\.pdf$/i, ""));
      formulario.append("file", archivo);
      await api.enviarFormulario(`/classes/${clase.id}/materials`, formulario);
    }
    return (await this.obtenerClase()) ?? claseDesdeApi(clase, null, null);
  }

  async invitar(aliasOCorreo: string): Promise<Clase> {
    const id = leerClaseId();
    if (!id) throw new Error("Primero crea tu clase");
    const alias = (aliasOCorreo.split("@")[0] ?? aliasOCorreo).trim();
    await api.post<MiembroDto[]>(`/classes/${id}/invitations`, { aliases: [alias] });
    const clase = await this.obtenerClase();
    if (!clase) throw new Error("No encontramos tu clase");
    return clase;
  }

  async obtenerDetalleAlumno(alias: string): Promise<DetalleAlumno | null> {
    const clase = await this.obtenerClase();
    const alumno = clase?.alumnos.find((item) => item.alias === alias.toLowerCase());
    if (!clase || !alumno?.personaId) return null;
    const dto = await api.get<DetalleEstudianteDto>(`/classes/${clase.id}/students/${alumno.personaId}`);
    return detalleDesdeApi(dto, alumno, clase);
  }

  async salirDeClase(): Promise<void> {
    await api.delete("/me/membership");
    guardarClaseId(null);
  }
}

function detalleDesdeApi(dto: DetalleEstudianteDto, alumno: AlumnoClase, clase: Clase): DetalleAlumno {
  const usos = (["hint_1", "hint_2", "step_by_step", "final"] as EscalonApi[]).map((paso) => {
    const veces = dto.help_by_step.find((uso) => uso.step === paso)?.count ?? 0;
    return {
      texto: `${NOMBRE_ESCALON[paso]} · ${veces === 1 ? "1 vez" : `${veces} veces`}`,
      usado: veces > 0,
    };
  });
  // Cada intento con ayuda empieza en la pista 1: así se estima el total de ejercicios.
  const conAyuda = dto.help_by_step.find((uso) => uso.step === "hint_1")?.count ?? 0;
  const aciertos = dto.total_answers ? Math.round((dto.correct_answers / dto.total_answers) * 100) : 0;
  const formato = dto.preferred_format ? nombreFormato(formatoDesdeApi(dto.preferred_format)) : null;
  const sugerencia = dto.most_failed_question
    ? `Repasa con ${dto.alias} la pregunta «${dto.most_failed_question}»${
        formato ? ` usando el formato ${formato.toLowerCase()}, el que más usa` : ""
      }.`
    : `${dto.alias} va bien. Propónle resolver el siguiente ejercicio sin IA.`;
  return {
    alumno: { ...alumno, nombre: dto.alias },
    clase: clase.nombre,
    usoEscalera: usos,
    resueltosSinIa: { hechos: dto.solved_without_ai, total: dto.solved_without_ai + conAyuda },
    competencias: [{ etiqueta: "Aciertos en las preguntas de la clase", porcentaje: aciertos }],
    // La API no comparte conversaciones con el docente.
    conversacion: [],
    sugerencia,
    esEjemplo: clase.esEjemplo,
  };
}
