// Cómo entra cada persona a FROBI: puerta de clase (docente o estudiante con código) o puerta libre.
export type ModoUso = "docente" | "estudiante-clase" | "autonomo";

export type PerfilAccesibilidadId = "baja-vision" | "sordera" | "neurodivergencia" | "movilidad";

// Quién respondió el asistente: la propia persona o alguien de confianza que la acompaña.
export type ConfiguradoPor = "yo" | "acompanante";

export interface Perfil {
  modo: ModoUso | null;
  codigoClase: string | null;
  perfiles: PerfilAccesibilidadId[];
  configuradoPor: ConfiguradoPor;
  vioIntro: boolean;
  vioAsistente: boolean;
}

export interface ResultadoCodigoClase {
  valido: boolean;
  nombreClase?: string;
  mensaje?: string;
}
