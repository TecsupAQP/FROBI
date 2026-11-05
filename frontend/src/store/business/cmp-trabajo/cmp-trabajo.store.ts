import { computed, ref } from "vue";
import { defineStore } from "pinia";
import type { WorkReview } from "@/core/shared/domain/view/claim-review.view";
import {
  obtenerBorradorEjemploService,
  revisarTrabajoService,
} from "@/core/trabajo/infraestructure/adapters/in/service/trabajo.service";

// Compartido por "Trae tu trabajo" (Figma · 14) y "Revisión de afirmaciones" (Figma · 15).
export const useCmpTrabajoStore = defineStore("CmpTrabajoStore", () => {
  const consigna = ref("");
  const borrador = ref("");
  const revision = ref<WorkReview | null>(null);
  const revisando = ref(false);

  const palabras = computed(() => borrador.value.trim().split(/\s+/).filter(Boolean).length);
  const puedeRevisar = computed(() => consigna.value.trim() !== "" && borrador.value.trim() !== "");

  const cargarEjemplo = async () => {
    if (consigna.value || borrador.value) return;
    const ejemplo = await obtenerBorradorEjemploService();
    consigna.value = ejemplo.consigna;
    borrador.value = ejemplo.borrador;
  };

  const revisar = async () => {
    revisando.value = true;
    try {
      revision.value = await revisarTrabajoService({ consigna: consigna.value, borrador: borrador.value });
    } finally {
      revisando.value = false;
    }
  };

  // Si se entra directo a la revisión, se revisa el borrador de ejemplo.
  const asegurarRevision = async () => {
    if (revision.value) return;
    await cargarEjemplo();
    await revisar();
  };

  return {
    borrador,
    consigna,
    palabras,
    puedeRevisar,
    revisando,
    revision,
    asegurarRevision,
    cargarEjemplo,
    revisar,
  };
});
