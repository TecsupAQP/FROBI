import type {
  AsistentePort,
  ConexionAsistente,
} from "@/core/asistente/infraestructure/ports/in/asistente.port";
import type {
  ConversacionAsistente,
  EstadoConexion,
  EventoAsistente,
  LineaChat,
} from "@/core/shared/domain/view/asistente.view";
import { API_URL, api, leerToken } from "@/core/shared/infraestructure/http/api.client";
import type { ConversacionDto } from "@/core/shared/infraestructure/http/api.dto";

// Cierre 4401: el token no vale (sesión vencida). No se reintenta.
const CIERRE_SIN_SESION = 4401;
const ESPERA_MAXIMA_MS = 15000;
// Mantiene viva la conexión detrás de proxies que cortan sockets inactivos.
const PING_MS = 25000;

const urlSocket = (): string => {
  const url = new URL(`${API_URL}/assistant/ws`, window.location.origin);
  url.protocol = url.protocol === "https:" ? "wss:" : "ws:";
  return url.toString();
};

let siguienteId = 0;
export const nuevoIdLinea = () => `linea-${Date.now()}-${siguienteId++}`;

export function conversacionDesdeApi(dto: ConversacionDto): ConversacionAsistente {
  return {
    habilitado: dto.enabled,
    preguntasRestantes: dto.questions_left,
    respondiendo: dto.answering,
    lineas: dto.lines.map<LineaChat>((linea) => ({
      id: nuevoIdLinea(),
      quien: linea.speaker === "person" ? "persona" : "frobi",
      texto: linea.text,
      estado: "lista",
    })),
  };
}

// GET y DELETE /assistant/conversation; las preguntas y respuestas van por WS /assistant/ws.
export class AsistenteUseCase implements AsistentePort {
  async leerConversacion(): Promise<ConversacionAsistente> {
    return conversacionDesdeApi(await api.get<ConversacionDto>("/assistant/conversation"));
  }

  async reiniciar(): Promise<void> {
    await api.delete("/assistant/conversation");
  }

  conectar(handlers: {
    alEvento: (evento: EventoAsistente) => void;
    alEstado: (estado: EstadoConexion) => void;
    alConectar: () => void;
  }): ConexionAsistente {
    let socket: WebSocket | null = null;
    let cerrado = false;
    let intentos = 0;
    let reintento: number | undefined;
    let ping: number | undefined;

    const abrir = () => {
      const token = leerToken();
      if (!token || cerrado) return;
      handlers.alEstado("conectando");
      const actual = new WebSocket(urlSocket());
      socket = actual;
      // El token va en el primer mensaje, no en la URL (no queda en registros del proxy).
      actual.onopen = () => actual.send(JSON.stringify({ type: "auth", token }));
      actual.onmessage = (mensaje) => {
        let evento: EventoAsistente;
        try {
          evento = JSON.parse(String(mensaje.data)) as EventoAsistente;
        } catch {
          return;
        }
        if (evento.type === "ready") {
          intentos = 0;
          handlers.alEstado("en-linea");
          handlers.alConectar();
          window.clearInterval(ping);
          ping = window.setInterval(() => actual.send(JSON.stringify({ type: "ping" })), PING_MS);
        }
        handlers.alEvento(evento);
      };
      actual.onclose = (cierre) => {
        window.clearInterval(ping);
        if (socket !== actual) return;
        socket = null;
        handlers.alEstado("sin-conexion");
        if (cerrado || cierre.code === CIERRE_SIN_SESION) return;
        const espera = Math.min(ESPERA_MAXIMA_MS, 1000 * 2 ** intentos);
        intentos += 1;
        reintento = window.setTimeout(abrir, espera);
      };
    };

    abrir();

    return {
      preguntar(pregunta: string, materialId: string | null): boolean {
        if (!socket || socket.readyState !== WebSocket.OPEN) return false;
        socket.send(JSON.stringify({ type: "ask", question: pregunta, material_id: materialId }));
        return true;
      },
      cerrar() {
        cerrado = true;
        window.clearTimeout(reintento);
        window.clearInterval(ping);
        socket?.close();
        socket = null;
      },
    };
  }
}
