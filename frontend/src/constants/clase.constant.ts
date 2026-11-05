import type { EstadoAlumno, TipoAlerta } from "@/core/shared/domain/view/clase.view";
import type { NombreIcono } from "@/constants/iconos.constant";

export interface DefinicionEstado {
  texto: string;
  detalle: string;
  tono: "exito" | "aviso" | "neutro";
  icono: NombreIcono;
}

// Estado de cada alumno: siempre icono + texto, nunca solo color.
export const ESTADO_ALUMNO: Record<EstadoAlumno, DefinicionEstado> = {
  "se-unio": { texto: "Se unió", detalle: "Entró con el código", tono: "exito", icono: "check" },
  invitado: { texto: "Invitación pendiente", detalle: "Recibió el enlace", tono: "aviso", icono: "alert" },
  salio: { texto: "Salió de la clase", detalle: "Ya no comparte su actividad", tono: "neutro", icono: "x" },
};

export const ALERTA_ALUMNO: Record<TipoAlerta, { tono: "exito" | "aviso"; icono: NombreIcono }> = {
  "va-bien": { tono: "exito", icono: "check" },
  "se-traba": { tono: "aviso", icono: "warn" },
};
