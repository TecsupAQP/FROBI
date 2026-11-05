import { ref } from "vue";
import { defineStore } from "pinia";
import type { PanelDocente } from "@/core/shared/domain/view/panel-docente.view";
import { obtenerPanelDocenteService } from "@/core/docente/infraestructure/adapters/in/service/docente.service";

export const useCmpDocenteStore = defineStore("CmpDocenteStore", () => {
  const panel = ref<PanelDocente | null>(null);
  const grupoId = ref("meca-1");

  const cargar = async () => {
    panel.value = await obtenerPanelDocenteService(grupoId.value);
  };

  const cambiarGrupo = async (id: string) => {
    grupoId.value = id;
    await cargar();
  };

  return { grupoId, panel, cambiarGrupo, cargar };
});
