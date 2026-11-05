import { ref } from "vue";
import { defineStore } from "pinia";
import type { PanelDocente } from "@/core/shared/domain/view/panel-docente.view";
import { obtenerPanelDocenteService } from "@/core/docente/infraestructure/adapters/in/service/docente.service";
import { elegirClaseService } from "@/core/clase/infraestructure/adapters/in/service/clase.service";
import { useCmpClaseStore } from "@/store/common/cmp-clase/cmp-clase.store";

export const useCmpDocenteStore = defineStore("CmpDocenteStore", () => {
  const panel = ref<PanelDocente | null>(null);
  const cargado = ref(false);
  const grupoId = ref("");

  const cargar = async () => {
    panel.value = await obtenerPanelDocenteService();
    grupoId.value = panel.value?.grupo.id ?? "";
    cargado.value = true;
  };

  // Cambia la clase que se ve: panel, alumnos, código y contenido pasan a ser los de esa clase.
  const cambiarGrupo = async (id: string) => {
    if (id === grupoId.value) return;
    elegirClaseService(id);
    grupoId.value = id;
    await Promise.all([cargar(), useCmpClaseStore().cargar(true)]);
    await useCmpClaseStore().cargarContenido();
  };

  return { cargado, grupoId, panel, cambiarGrupo, cargar };
});
