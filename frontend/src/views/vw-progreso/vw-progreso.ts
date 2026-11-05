import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpProgreso from "@/components/business/cmp-progreso/cmp-progreso.vue";
import useCmpSesion from "@/composables/common/cmp-sesion/cmp-sesion.composable";

export default defineComponent({
  name: "VwProgreso",
  components: { CmpLayoutPagina, CmpProgreso },
  setup() {
    const { estudiante } = useCmpSesion();

    return { estudiante };
  },
});
