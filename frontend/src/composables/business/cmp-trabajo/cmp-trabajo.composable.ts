import { storeToRefs } from "pinia";
import { useCmpTrabajoStore } from "@/store/business/cmp-trabajo/cmp-trabajo.store";

function useCmpTrabajo() {
  const store = useCmpTrabajoStore();
  const { borrador, consigna, palabras, puedeRevisar, revisando, revision } = storeToRefs(store);

  return {
    borrador,
    consigna,
    palabras,
    puedeRevisar,
    revisando,
    revision,

    revisar: store.revisar,
  };
}

export default useCmpTrabajo;
