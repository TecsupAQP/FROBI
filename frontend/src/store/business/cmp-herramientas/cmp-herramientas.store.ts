import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { NecesidadId, RecomendacionHerramientas } from "@/core/shared/domain/view/tool.view";
import { obtenerRecomendacionService } from "@/core/herramientas/infraestructure/adapters/in/service/herramientas.service";
import { useCmpTrabajoStore } from "@/store/business/cmp-trabajo/cmp-trabajo.store";

export const useCmpHerramientasStore = defineStore("CmpHerramientasStore", () => {
  const recomendacion = ref<RecomendacionHerramientas | null>(null);
  const necesidad = ref<NecesidadId>("verify_source");

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

  // Se recomienda para la primera afirmación revisada que no tiene respaldo en la guía.
  const cargar = async () => {
    const afirmaciones =
      useCmpTrabajoStore().revision?.secciones.flatMap((seccion) => seccion.afirmaciones) ?? [];
    const elegida =
      afirmaciones.find((afirmacion) => afirmacion.estado !== "con-respaldo") ?? afirmaciones[0] ?? null;
    recomendacion.value = await obtenerRecomendacionService(
      elegida ? { id: elegida.id, texto: elegida.texto } : null,
    );
    necesidad.value = recomendacion.value.necesidadSugerida;
  };

  const elegirNecesidad = (id: NecesidadId) => {
    necesidad.value = id;
  };

  return { necesidad, nombreNecesidad, otras, recomendacion, recomendada, cargar, elegirNecesidad };
});
