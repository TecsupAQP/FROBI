import { EstadoCargaEnum } from "@/core/shared/application/enum/estado-carga.enum";

const DEMORA_MS = 450;

export class SinConexionError extends Error {
  constructor() {
    super("Sin conexión");
    this.name = "SinConexionError";
  }
}

// Escenario forzado para la maqueta: ?estado=vacio | error-respaldo | sin-conexion | cargando
export function escenarioSimulado(): EstadoCargaEnum {
  const valor = new URLSearchParams(window.location.search).get("estado");
  const escenarios = Object.values(EstadoCargaEnum) as string[];
  return valor && escenarios.includes(valor) ? (valor as EstadoCargaEnum) : EstadoCargaEnum.LISTO;
}

export function esperar(ms: number = DEMORA_MS): Promise<void> {
  return new Promise((resolver) => setTimeout(resolver, ms));
}

// Devuelve una copia del mock tras una pequeña demora, como haría el backend.
export async function respuestaSimulada<T>(datos: T, ms?: number): Promise<T> {
  const escenario = escenarioSimulado();
  if (escenario === EstadoCargaEnum.CARGANDO) {
    await new Promise<never>(() => undefined);
  }
  await esperar(ms);
  if (escenario === EstadoCargaEnum.SIN_CONEXION) {
    throw new SinConexionError();
  }
  // Copia en JSON: los datos pueden llegar como objetos reactivos de Vue, que structuredClone no acepta.
  return datos === undefined ? datos : (JSON.parse(JSON.stringify(datos)) as T);
}
