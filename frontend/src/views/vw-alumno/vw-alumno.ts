import { computed, defineComponent } from "vue";
import { useRoute } from "vue-router";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpAlumno from "@/components/business/cmp-alumno/cmp-alumno.vue";

export default defineComponent({
  name: "VwAlumno",
  components: { CmpLayoutPagina, CmpAlumno },
  setup() {
    const route = useRoute();

    const alias = computed(() => (typeof route.params.alias === "string" ? route.params.alias : ""));

    return { alias };
  },
});
