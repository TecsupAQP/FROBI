import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { WorkReview } from "@/core/shared/domain/view/claim-review.view";
import { revisarTrabajoService } from "@/core/trabajo/infraestructure/adapters/in/service/trabajo.service";

// Compartido por "Trae tu trabajo" (Figma · 14) y "Revisión de afirmaciones" (Figma · 15).
export const useCmpTrabajoStore = defineStore("CmpTrabajoStore", () => {
  const consigna = ref("");
  const borrador = ref("");
  const revision = ref<WorkReview | null>(null);
  const revisando = ref(false);

  const palabras = computed(() => borrador.value.trim().split(/\s+/).filter(Boolean).length);
  const puedeRevisar = computed(() => consigna.value.trim() !== "" && borrador.value.trim() !== "");

  const revisar = async () => {
    revisando.value = true;
    try {
      revision.value = await revisarTrabajoService({ consigna: consigna.value, borrador: borrador.value });
    } finally {
      revisando.value = false;
    }
  };

  return {
    borrador,
    consigna,
    palabras,
    puedeRevisar,
    revisando,
    revision,
    revisar,
  };
});
