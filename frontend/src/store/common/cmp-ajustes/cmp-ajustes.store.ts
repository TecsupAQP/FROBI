import { ref } from "vue";
import { defineStore } from "pinia";
import type { AjusteId, Ajustes, Idioma } from "@/core/shared/domain/view/ajustes.view";
import {
  guardarAjustesService,
  obtenerAjustesService,
  obtenerIdiomasService,
} from "@/core/perfil/infraestructure/adapters/in/service/perfil.service";
import { AJUSTES_INICIALES } from "@/constants/perfil.constant";

// Ajustes de accesibilidad e idioma (Figma · 24). Se aplican en <html> con useAplicarAjustes.
export const useCmpAjustesStore = defineStore("CmpAjustesStore", () => {
  const ajustes = ref<Ajustes>(structuredClone(AJUSTES_INICIALES));
  const idiomas = ref<Idioma[]>([]);
  const cargado = ref(false);

  const cargar = async () => {
    if (cargado.value) return;
    const [guardados, disponibles] = await Promise.all([obtenerAjustesService(), obtenerIdiomasService()]);
    ajustes.value = guardados;
    idiomas.value = disponibles;
    cargado.value = true;
  };

  // Vuelve a leer de la API (por ejemplo, después del asistente, que aplica los ajustes de cada perfil).
  const recargar = async () => {
    cargado.value = false;
    await cargar();
  };

  const reiniciar = () => {
    ajustes.value = structuredClone(AJUSTES_INICIALES);
    cargado.value = false;
  };

  const guardar = () => guardarAjustesService(JSON.parse(JSON.stringify(ajustes.value)) as Ajustes);

  const alternar = (id: AjusteId) => {
    ajustes.value.activos[id] = !ajustes.value.activos[id];
    guardar();
  };

  // El asistente y el perfil de accesibilidad encienden varios ajustes a la vez.
  const activarVarios = (ids: AjusteId[], reemplazar = false) => {
    if (reemplazar) {
      (Object.keys(ajustes.value.activos) as AjusteId[]).forEach((id) => (ajustes.value.activos[id] = false));
    }
    ids.forEach((id) => (ajustes.value.activos[id] = true));
    guardar();
  };

  return { ajustes, cargado, idiomas, activarVarios, alternar, cargar, recargar, reiniciar };
});
