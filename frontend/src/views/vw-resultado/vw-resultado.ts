import { computed, defineComponent, ref } from "vue";
import { useRoute } from "vue-router";
import VButton from "@/components/base/v-button/v-button.vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpResultado from "@/components/business/cmp-resultado/cmp-resultado.vue";
import { esFormatoValido } from "@/constants/formatos.constant";
import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";
import { RutaEnum } from "@/enums/ruta.enum";

export default defineComponent({
  name: "VwResultado",
  components: { VButton, CmpLayoutPagina, CmpResultado },
  setup() {
    const PREFIX = "vw-resultado";

    const route = useRoute();

    const reintentos = ref(0);

    const formato = computed<FormatoId>(() =>
      esFormatoValido(route.params.formato) ? route.params.formato : "mapa-visual",
    );

    return { RutaEnum, PREFIX, reintentos, formato };
  },
});
