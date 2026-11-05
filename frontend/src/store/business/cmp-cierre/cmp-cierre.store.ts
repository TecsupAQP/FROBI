import { ref } from "vue";
import { defineStore } from "pinia";
import type { ResumenCierre } from "@/core/shared/domain/view/cierre.view";
import { obtenerResumenCierreService } from "@/core/cierre/infraestructure/adapters/in/service/cierre.service";

export const useCmpCierreStore = defineStore("CmpCierreStore", () => {
  const resumen = ref<ResumenCierre | null>(null);

  const cargar = async () => {
    resumen.value = await obtenerResumenCierreService();
  };

  return { resumen, cargar };
});
