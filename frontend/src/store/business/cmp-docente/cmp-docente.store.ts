import { ref } from "vue";
import { defineStore } from "pinia";
import type { PanelDocente } from "@/core/shared/domain/view/panel-docente.view";
import { obtenerPanelDocenteService } from "@/core/docente/infraestructure/adapters/in/service/docente.service";

export const useCmpDocenteStore = defineStore("CmpDocenteStore", () => {
  const panel = ref<PanelDocente | null>(null);
  const cargado = ref(false);
  const grupoId = ref("");

  const cargar = async () => {
    panel.value = await obtenerPanelDocenteService();
    grupoId.value = panel.value?.grupo.id ?? "";
    cargado.value = true;
  };

  // Hoy el docente tiene una sola clase; el selector queda listo para varias.
  const cambiarGrupo = async (id: string) => {
    grupoId.value = id;
    await cargar();
  };

  return { cargado, grupoId, panel, cambiarGrupo, cargar };
});
