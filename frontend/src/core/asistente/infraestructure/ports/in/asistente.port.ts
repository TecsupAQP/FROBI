import type {
  ConversacionAsistente,
  EstadoConexion,
  EventoAsistente,
} from "@/core/shared/domain/view/asistente.view";

export interface ConexionAsistente {
  // false si el socket no está abierto (la pregunta no salió).
  preguntar(pregunta: string, materialId: string | null): boolean;
  cerrar(): void;
}

export interface AsistentePort {
  leerConversacion(): Promise<ConversacionAsistente>;
  // Empieza una conversación nueva (también se limpia en las otras pestañas abiertas).
  reiniciar(): Promise<void>;
  // Abre el WebSocket y se reconecta solo. alConectar avisa cada vez que vuelve a estar en línea.
  conectar(handlers: {
    alEvento: (evento: EventoAsistente) => void;
    alEstado: (estado: EstadoConexion) => void;
    alConectar: () => void;
  }): ConexionAsistente;
}
