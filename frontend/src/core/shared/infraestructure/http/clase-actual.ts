import { api } from "@/core/shared/infraestructure/http/api.client";
import type { ClaseDto, YoDto } from "@/core/shared/infraestructure/http/api.dto";

// El docente recuerda la clase que creó; si no, se usa la membresía activa de /me.
const CLAVE_CLASE = "frobi-clase-id";

export function leerClaseId(): string | null {
  try {
    return localStorage.getItem(CLAVE_CLASE);
  } catch {
    return null;
  }
}

export function guardarClaseId(id: string | null): void {
  try {
    if (id) localStorage.setItem(CLAVE_CLASE, id);
    else localStorage.removeItem(CLAVE_CLASE);
  } catch {
    // Sin almacenamiento: la clase se vuelve a buscar en /me.
  }
}

// El docente puede tener varias clases: se usa la elegida si sigue siendo suya; si no, la más
// reciente (GET /classes). El estudiante usa la clase a la que está unido.
export async function claseActualId(yo?: YoDto): Promise<string | null> {
  const persona = yo ?? (await api.get<YoDto>("/me"));
  if (persona.person.role !== "teacher") return persona.membership?.class_id ?? null;
  const clases = await api.get<ClaseDto[]>("/classes");
  const guardada = leerClaseId();
  if (guardada && clases.some((clase) => clase.id === guardada)) return guardada;
  const reciente = clases[0]?.id ?? null;
  guardarClaseId(reciente);
  return reciente;
}
