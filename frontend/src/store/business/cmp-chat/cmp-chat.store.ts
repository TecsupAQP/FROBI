import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { EstadoConexion, EventoAsistente, LineaChat } from "@/core/shared/domain/view/asistente.view";
import type { ConexionAsistente } from "@/core/asistente/infraestructure/ports/in/asistente.port";
import {
  conectarAsistenteService,
  leerConversacionService,
  reiniciarConversacionService,
} from "@/core/asistente/infraestructure/adapters/in/service/asistente.service";
import { nuevoIdLinea } from "@/core/asistente/application/use-case/asistente.use-case";
import { materialGuardadoId } from "@/core/shared/infraestructure/http/contexto-estudio";
import { esErrorApi } from "@/core/shared/infraestructure/http/api.client";

export const useCmpChatStore = defineStore("CmpChatStore", () => {
  const lineas = ref<LineaChat[]>([]);
  const conexion = ref<EstadoConexion>("conectando");
  const habilitado = ref(true);
  const preguntasRestantes = ref<number | null>(null);
  const respondiendo = ref(false);
  // Lo que está consultando ahora («Revisando tu progreso…»).
  const consultando = ref<string | null>(null);
  const error = ref<string | null>(null);
  // Texto que vuelve al campo si la pregunta no se pudo enviar.
  const borrador = ref("");

  let socket: ConexionAsistente | null = null;
  // Si el socket se cortó a mitad de una respuesta, al terminar se trae la versión guardada.
  let faltaUnaParte = false;

  const enCurso = computed(() => lineas.value.find((linea) => linea.estado === "escribiendo"));

  const sincronizar = async () => {
    try {
      const conversacion = await leerConversacionService();
      habilitado.value = conversacion.habilitado;
      preguntasRestantes.value = conversacion.preguntasRestantes;
      respondiendo.value = conversacion.respondiendo;
      // Si se está respondiendo, el texto que siga llegando se suma a una línea nueva.
      lineas.value = conversacion.lineas;
    } catch {
      // Sin conexión: se conserva lo que ya se ve en pantalla.
    }
  };

  const terminarRespuesta = (estado: LineaChat["estado"]) => {
    const linea = enCurso.value;
    if (linea) linea.estado = estado;
    respondiendo.value = false;
    consultando.value = null;
  };

  const alEvento = (evento: EventoAsistente) => {
    switch (evento.type) {
      case "question": {
        const pendiente = lineas.value.find((l) => l.estado === "pendiente" && l.texto === evento.text);
        if (pendiente) pendiente.estado = "lista";
        else lineas.value.push({ id: nuevoIdLinea(), quien: "persona", texto: evento.text, estado: "lista" });
        respondiendo.value = true;
        error.value = null;
        break;
      }
      case "tool":
        respondiendo.value = true;
        consultando.value = evento.status;
        break;
      case "text": {
        respondiendo.value = true;
        consultando.value = null;
        const linea = enCurso.value;
        if (linea) linea.texto += evento.text;
        else
          lineas.value.push({
            id: nuevoIdLinea(),
            quien: "frobi",
            texto: evento.text,
            estado: "escribiendo",
          });
        break;
      }
      case "done":
        terminarRespuesta(evento.fallback ? "respaldo" : "lista");
        preguntasRestantes.value = evento.questions_left;
        if (faltaUnaParte && !evento.fallback) void sincronizar();
        faltaUnaParte = false;
        break;
      case "restarted":
        lineas.value = [];
        respondiendo.value = false;
        consultando.value = null;
        void sincronizar();
        break;
      case "error": {
        // Solo llega al socket que preguntó: la pregunta no se aceptó y vuelve al campo.
        let pendiente = lineas.value.length - 1;
        while (pendiente >= 0 && lineas.value[pendiente].estado !== "pendiente") pendiente -= 1;
        if (pendiente >= 0) {
          borrador.value = lineas.value[pendiente].texto;
          lineas.value.splice(pendiente, 1);
        }
        error.value = evento.message;
        break;
      }
      default:
        break;
    }
  };

  const abrir = async () => {
    error.value = null;
    await sincronizar();
    if (socket) return;
    socket = conectarAsistenteService({
      alEvento,
      alEstado: (estado) => (conexion.value = estado),
      // Al reconectar se pudo perder parte de una respuesta: se trae la conversación guardada.
      alConectar: () => {
        faltaUnaParte = respondiendo.value;
        void sincronizar();
      },
    });
  };

  const cerrar = () => {
    socket?.cerrar();
    socket = null;
  };

  const enviar = (texto: string): boolean => {
    const pregunta = texto.trim();
    if (!pregunta || respondiendo.value) return false;
    if (!socket?.preguntar(pregunta, materialGuardadoId())) {
      error.value = "No hay conexión. Espera un momento: me estoy reconectando.";
      return false;
    }
    error.value = null;
    borrador.value = "";
    lineas.value.push({ id: nuevoIdLinea(), quien: "persona", texto: pregunta, estado: "pendiente" });
    return true;
  };

  const nuevaConversacion = async () => {
    try {
      await reiniciarConversacionService();
      lineas.value = [];
      error.value = null;
      await sincronizar();
    } catch (e) {
      error.value = esErrorApi(e) ? e.detalle : "No pude empezar una conversación nueva.";
    }
  };

  return {
    borrador,
    conexion,
    consultando,
    error,
    habilitado,
    lineas,
    preguntasRestantes,
    respondiendo,
    abrir,
    cerrar,
    enviar,
    nuevaConversacion,
  };
});
