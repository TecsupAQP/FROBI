import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { NecesidadId, RecomendacionHerramientas } from "@/core/shared/domain/view/tool.view";
import { obtenerRecomendacionService } from "@/core/herramientas/infraestructure/adapters/in/service/herramientas.service";

export const useCmpHerramientasStore = defineStore("CmpHerramientasStore", () => {
  const recomendacion = ref<RecomendacionHerramientas | null>(null);
  const necesidad = ref<NecesidadId>("verificar-dato");

  // La primera herramienta del catálogo que cubre la necesidad elegida es la recomendada.
  const recomendada = computed(
    () =>
      recomendacion.value?.catalogo.find((herramienta) =>
        herramienta.necesidades.includes(necesidad.value),
      ) ?? null,
  );
  const otras = computed(
    () =>
      recomendacion.value?.catalogo.filter((herramienta) => herramienta.id !== recomendada.value?.id) ?? [],
  );
  const nombreNecesidad = computed(
    () => recomendacion.value?.necesidades.find((item) => item.id === necesidad.value)?.nombre ?? "",
  );

  const cargar = async () => {
    recomendacion.value = await obtenerRecomendacionService("af-vidrio");
  };

  const elegirNecesidad = (id: NecesidadId) => {
    necesidad.value = id;
  };

  return { necesidad, nombreNecesidad, otras, recomendacion, recomendada, cargar, elegirNecesidad };
});
