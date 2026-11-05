import { storeToRefs } from "pinia";
import { useCmpLoginStore } from "@/store/business/cmp-login/cmp-login.store";

function useCmpLogin() {
  const store = useCmpLoginStore();
  const { alias, carrera, carreras, codigoClase, enviando, errores, nombreClase, rol } = storeToRefs(store);

  return {
    alias,
    carrera,
    carreras,
    codigoClase,
    enviando,
    errores,
    nombreClase,
    rol,

    cargarCarreras: store.cargarCarreras,
    entrar: store.entrar,
  };
}

export default useCmpLogin;
