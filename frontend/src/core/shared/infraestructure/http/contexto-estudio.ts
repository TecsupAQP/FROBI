import { SinGuiaError } from "@/core/shared/application/util/errores.util";
import { api } from "@/core/shared/infraestructure/http/api.client";
import type {
  AdaptacionDto,
  MaterialClaseDto,
  MaterialResumenDto,
  YoDto,
} from "@/core/shared/infraestructure/http/api.dto";

// Qué material estudia la persona y con qué adaptación. La escalera de ayuda y las preguntas
// se piden sobre una adaptación concreta (adaptation_id), así que se recuerdan entre pantallas.
const CLAVE_MATERIAL = "frobi-material-id";
const CLAVE_ADAPTACION = "frobi-adaptacion-id";

const leer = (clave: string): string | null => {
  try {
    return localStorage.getItem(clave);
  } catch {
    return null;
  }
};

const escribir = (clave: string, valor: string | null) => {
  try {
    if (valor) localStorage.setItem(clave, valor);
    else localStorage.removeItem(clave);
  } catch {
    // Sin almacenamiento: al recargar se vuelve a buscar tu guía más reciente.
  }
};

// Por defecto: si la persona está en una clase, el material más reciente de su docente; si no,
// su guía propia más reciente. La de ejemplo nunca se elige sola (solo si la pide).
export async function materialActualId(): Promise<string> {
  const guardado = leer(CLAVE_MATERIAL);
  if (guardado) return guardado;
  const [yo, guias] = await Promise.all([
    api.get<YoDto>("/me"),
    api.get<MaterialResumenDto[]>("/materials/guides"),
  ]);
  const deClase = yo.membership
    ? (await api.get<MaterialClaseDto[]>(`/classes/${yo.membership.class_id}/materials`))[0]
    : undefined;
  const elegido = deClase?.id ?? guias.find((guia) => guia.source !== "sample")?.id;
  if (!elegido) throw new SinGuiaError();
  escribir(CLAVE_MATERIAL, elegido);
  return elegido;
}

// El material guardado ya no se puede ver (por ejemplo, la persona salió de la clase).
export function olvidarMaterial(): void {
  escribir(CLAVE_MATERIAL, null);
  escribir(CLAVE_ADAPTACION, null);
}

// Para las rutas que necesitan una guía (guía, resultado, escalera, verificación…).
export async function hayGuiaActual(): Promise<boolean> {
  try {
    await materialActualId();
    return true;
  } catch (error) {
    if (error instanceof SinGuiaError) return false;
    throw error;
  }
}

// La guía que la persona tiene abierta, sin pedirla a la API (null si aún no eligió una).
export function materialGuardadoId(): string | null {
  return leer(CLAVE_MATERIAL);
}

export function elegirMaterial(id: string): void {
  if (leer(CLAVE_MATERIAL) === id) return;
  escribir(CLAVE_MATERIAL, id);
  escribir(CLAVE_ADAPTACION, null);
}

export function recordarAdaptacion(id: string): void {
  escribir(CLAVE_ADAPTACION, id);
}

// La última adaptación vista; si aún no hay, se pide una en lectura fácil (la API la guarda en caché).
export async function adaptacionActualId(): Promise<string> {
  const guardada = leer(CLAVE_ADAPTACION);
  if (guardada) return guardada;
  const material = await materialActualId();
  const adaptacion = await api.post<AdaptacionDto>(`/materials/${material}/adaptations`, {
    format: "easy_read",
  });
  recordarAdaptacion(adaptacion.id);
  return adaptacion.id;
}

export function olvidarContextoEstudio(): void {
  escribir(CLAVE_MATERIAL, null);
  escribir(CLAVE_ADAPTACION, null);
}
