import { defineComponent } from "vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpPerfilAccesibilidad from "@/components/business/cmp-perfil-accesibilidad/cmp-perfil-accesibilidad.vue";

export default defineComponent({
  name: "VwPerfilAccesibilidad",
  components: { CmpLayoutPagina, CmpPerfilAccesibilidad },
  setup() {
    return {};
  },
});
