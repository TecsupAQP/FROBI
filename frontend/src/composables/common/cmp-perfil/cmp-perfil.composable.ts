import { storeToRefs } from "pinia";
import { useCmpPerfilStore } from "@/store/common/cmp-perfil/cmp-perfil.store";

function useCmpPerfil() {
  const store = useCmpPerfilStore();
  const { cargado, guardando, perfil } = storeToRefs(store);

  return {
    cargado,
    guardando,
    perfil,

    alternarPerfil: store.alternarPerfil,
    cargar: store.cargar,
    elegirConfiguradoPor: store.elegirConfiguradoPor,
    elegirModo: store.elegirModo,
    guardar: store.guardar,
    marcarAsistenteVisto: store.marcarAsistenteVisto,
    marcarIntroVista: store.marcarIntroVista,
    reiniciarAsistente: store.reiniciarAsistente,
    validarCodigo: store.validarCodigo,
  };
}

export default useCmpPerfil;
