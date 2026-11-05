import { SinConexionError } from "@/core/shared/application/util/errores.util";

// Cliente HTTP de la API de FROBI (backend FastAPI, prefijo /api/v1).
export const API_URL: string = import.meta.env.VITE_API_URL || "http://localhost:8000/api/v1";

const CLAVE_TOKEN = "frobi-token";

// Error de la API en formato application/problem+json (RFC 9457). `codigo` es estable:
// "Classrooms.InvalidCode", "Tutoring.FinalLocked", "Identity.Unauthenticated"…
export class ApiError extends Error {
  constructor(
    readonly status: number,
    readonly codigo: string,
    readonly detalle: string,
  ) {
    super(detalle);
    this.name = "ApiError";
  }
}

export const esErrorApi = (error: unknown, codigo?: string): error is ApiError =>
  error instanceof ApiError && (codigo === undefined || error.codigo === codigo);

export function leerToken(): string | null {
  try {
    return localStorage.getItem(CLAVE_TOKEN);
  } catch {
    return null;
  }
}

export function guardarToken(token: string | null): void {
  try {
    if (token) localStorage.setItem(CLAVE_TOKEN, token);
    else localStorage.removeItem(CLAVE_TOKEN);
  } catch {
    // Sin almacenamiento: el token no sobrevive a una recarga.
  }
}

// La capa de rutas registra qué hacer cuando la sesión vence (ir a "Entrar").
let alPerderSesion: () => void = () => undefined;
export const registrarAlPerderSesion = (accion: () => void) => {
  alPerderSesion = accion;
};

interface OpcionesPeticion {
  cuerpo?: unknown;
  formulario?: FormData;
  consulta?: Record<string, string | undefined>;
}

async function peticion<T>(metodo: string, ruta: string, opciones: OpcionesPeticion = {}): Promise<T> {
  // La base permite una VITE_API_URL relativa ("/api/v1") cuando el front y la API comparten dominio.
  const url = new URL(API_URL + ruta, window.location.origin);
  Object.entries(opciones.consulta ?? {}).forEach(([clave, valor]) => {
    if (valor !== undefined) url.searchParams.set(clave, valor);
  });

  const cabeceras: Record<string, string> = { Accept: "application/json" };
  const token = leerToken();
  if (token) cabeceras.Authorization = `Bearer ${token}`;
  let cuerpo: BodyInit | undefined;
  if (opciones.formulario) {
    cuerpo = opciones.formulario;
  } else if (opciones.cuerpo !== undefined) {
    cabeceras["Content-Type"] = "application/json";
    cuerpo = JSON.stringify(opciones.cuerpo);
  }

  let respuesta: Response;
  try {
    respuesta = await fetch(url, { method: metodo, headers: cabeceras, body: cuerpo });
  } catch {
    throw new SinConexionError();
  }

  if (respuesta.status === 204) return undefined as T;
  const datos: unknown = await respuesta.json().catch(() => null);
  if (!respuesta.ok) {
    const problema = (datos ?? {}) as { code?: string; detail?: string; title?: string };
    const error = new ApiError(
      respuesta.status,
      problema.code ?? `Http.${respuesta.status}`,
      problema.detail ?? problema.title ?? "Algo salió mal. Inténtalo de nuevo.",
    );
    if (respuesta.status === 401) {
      guardarToken(null);
      alPerderSesion();
    }
    throw error;
  }
  return datos as T;
}

export const api = {
  get: <T>(ruta: string, consulta?: OpcionesPeticion["consulta"]) => peticion<T>("GET", ruta, { consulta }),
  post: <T>(ruta: string, cuerpo?: unknown) => peticion<T>("POST", ruta, { cuerpo }),
  patch: <T>(ruta: string, cuerpo: unknown) => peticion<T>("PATCH", ruta, { cuerpo }),
  delete: <T = void>(ruta: string) => peticion<T>("DELETE", ruta),
  enviarFormulario: <T>(ruta: string, formulario: FormData) => peticion<T>("POST", ruta, { formulario }),
};
