import { storeToRefs } from "pinia";
import { useCmpPideloTuStore } from "@/store/business/cmp-pidelo-tu/cmp-pidelo-tu.store";

function useCmpPideloTu() {
  const store = useCmpPideloTuStore();
  const { autonomia, evaluacion, fase, instruccion, mejorada, piezasEscritas, plantilla, puedePedir } =
    storeToRefs(store);

  return {
    autonomia,
    evaluacion,
    fase,
    instruccion,
    mejorada,
    piezasEscritas,
    plantilla,
    puedePedir,

    anadirEjemplo: store.anadirEjemplo,
    iniciar: store.iniciar,
    mejorarInstruccion: store.mejorarInstruccion,
    pedirALaIA: store.pedirALaIA,
    probarOtra: store.probarOtra,
    usarPlantilla: store.usarPlantilla,
  };
}

export default useCmpPideloTu;
