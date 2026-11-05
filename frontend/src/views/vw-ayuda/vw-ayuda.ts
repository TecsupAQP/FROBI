import { computed, defineComponent } from "vue";
import { useRoute } from "vue-router";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpEscalera from "@/components/business/cmp-escalera/cmp-escalera.vue";
import { TAREA_EJEMPLO } from "@/enums/ruta.enum";

export default defineComponent({
  name: "VwAyuda",
  components: { CmpLayoutPagina, CmpEscalera },
  setup() {
    const route = useRoute();

    const tareaId = computed(() =>
      typeof route.params.tarea === "string" ? route.params.tarea : TAREA_EJEMPLO,
    );

    return { tareaId };
  },
});
