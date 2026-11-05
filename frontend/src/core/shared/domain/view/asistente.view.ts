// Chat privado con FROBI (M14). Cada persona conversa sola con el asistente.
export type QuienHabla = "persona" | "frobi";

export interface LineaChat {
  id: string;
  quien: QuienHabla;
  texto: string;
  // "escribiendo": llega en vivo; "respaldo": respuesta fija porque la IA no estaba disponible;
  // "pendiente": la pregunta se envió y el servidor aún no la confirma.
  estado: "lista" | "escribiendo" | "respaldo" | "pendiente";
}

export interface ConversacionAsistente {
  habilitado: boolean;
  lineas: LineaChat[];
  preguntasRestantes: number;
  respondiendo: boolean;
}

export type EstadoConexion = "conectando" | "en-linea" | "sin-conexion";

// Lo que envía el servidor por el WebSocket.
export type EventoAsistente =
  | { type: "ready" }
  | { type: "question"; text: string }
  | { type: "tool"; status: string }
  | { type: "text"; text: string }
  | { type: "done"; fallback: boolean; questions_left: number }
  | { type: "restarted" }
  | { type: "error"; code: string; message: string }
  | { type: "pong" };
