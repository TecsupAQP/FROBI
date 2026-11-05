import { computed, defineComponent } from "vue";
import { useRoute } from "vue-router";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpSinIa from "@/components/business/cmp-sin-ia/cmp-sin-ia.vue";
import { TAREA_EJEMPLO } from "@/enums/ruta.enum";

export default defineComponent({
  name: "VwSinIa",
  components: { CmpLayoutPagina, CmpSinIa },
  setup() {
    const route = useRoute();

    const tareaId = computed(() =>
      typeof route.params.tarea === "string" ? route.params.tarea : TAREA_EJEMPLO,
    );

    return { tareaId };
  },
});
