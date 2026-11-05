import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpInicio from "@/components/business/cmp-inicio/cmp-inicio.vue";
import useCmpSesion from "@/composables/common/cmp-sesion/cmp-sesion.composable";

export default defineComponent({
  name: "VwInicio",
  components: { CmpLayoutPagina, CmpInicio },
  setup() {
    const { estudiante } = useCmpSesion();

    return { estudiante };
  },
});
