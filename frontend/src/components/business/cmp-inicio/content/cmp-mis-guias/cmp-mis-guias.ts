import { defineComponent, type PropType } from "vue";
import VButton from "@/components/base/v-button/v-button.vue";
import VChip from "@/components/base/v-chip/v-chip.vue";
import VIcon from "@/components/base/v-icon/v-icon.vue";
import VProgressBar from "@/components/base/v-progress-bar/v-progress-bar.vue";
import type { NombreIcono } from "@/constants/iconos.constant";
import type { GuiaDeClase, GuiaResumen } from "@/core/shared/domain/view/material.view";

export default defineComponent({
  name: "CmpMisGuias",
  components: { VButton, VChip, VIcon, VProgressBar },
  props: {
    guias: { type: Array as PropType<GuiaResumen[]>, required: true },
    // Id de la guía que se está abriendo, para deshabilitar los botones mientras tanto.
    eligiendo: { type: String as PropType<string | null>, default: null },
    titulo: { type: String, default: "Mis guías" },
    descripcion: {
      type: String,
      default: "Todas las que subiste quedan guardadas. Elige con cuál estudiar.",
    },
    // Para los ids de los títulos cuando hay más de una lista en la página.
    prefijoId: { type: String, default: "mis-guias" },
  },
  emits: {
    elegir: (_id: string) => true,
    // Guía con tareas: abrir una tarea en la escalera de ayuda.
    resolver: (_guiaId: string, _tareaRef: string) => true,
    // Guía de estudio: la evaluación final de la IA.
    evaluar: (_guiaId: string) => true,
  },
  setup() {
    const PREFIX = "cmp-mis-guias";

    const ICONOS: Record<GuiaResumen["origen"], NombreIcono> = {
      ejemplo: "book",
      pdf: "file",
      texto: "type",
      clase: "users",
    };

    const ORIGENES: Record<GuiaResumen["origen"], string> = {
      ejemplo: "Guía de ejemplo",
      pdf: "PDF que subiste",
      texto: "Texto que pegaste",
      clase: "Lo subió tu docente",
    };

    // El avance en palabras (también es el texto de la barra para lectores de pantalla).
    const resumenAvance = (clase: GuiaDeClase): string => {
      if (clase.modo === "tareas") {
        const hechas = clase.tareas.filter((tarea) => tarea.hecha).length;
        return `${hechas} de ${clase.tareas.length} ${clase.tareas.length === 1 ? "tarea hecha" : "tareas hechas"}`;
      }
      return clase.evaluacion
        ? `Evaluación final: ${clase.evaluacion.aciertos} de ${clase.evaluacion.total} respuestas correctas`
        : "Guía de estudio: al terminar, haz la evaluación final";
    };

    return { PREFIX, ICONOS, ORIGENES, resumenAvance };
  },
});
