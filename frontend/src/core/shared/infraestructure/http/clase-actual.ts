import { api } from "@/core/shared/infraestructure/http/api.client";
import type { YoDto } from "@/core/shared/infraestructure/http/api.dto";

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

export async function claseActualId(yo?: YoDto): Promise<string | null> {
  const guardada = leerClaseId();
  if (guardada) return guardada;
  return (yo ?? (await api.get<YoDto>("/me"))).membership?.class_id ?? null;
}
