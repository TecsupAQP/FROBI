import { storeToRefs } from "pinia";
import { useCmpChatStore } from "@/store/business/cmp-chat/cmp-chat.store";

function useCmpChat() {
  const store = useCmpChatStore();
  const { borrador, conexion, consultando, error, habilitado, lineas, preguntasRestantes, respondiendo } =
    storeToRefs(store);

  return {
    borrador,
    conexion,
    consultando,
    error,
    habilitado,
    lineas,
    preguntasRestantes,
    respondiendo,

    abrir: store.abrir,
    cerrar: store.cerrar,
    enviar: store.enviar,
    nuevaConversacion: store.nuevaConversacion,
  };
}

export default useCmpChat;
