import { computed, defineComponent, ref } from "vue";
import { useRoute } from "vue-router";
import VButton from "@/components/base/v-button/v-button.vue";
import CmpLayoutPagina from "@/components/common/cmp-layout-pagina/cmp-layout-pagina.vue";
import CmpResultado from "@/components/business/cmp-resultado/cmp-resultado.vue";
import { esFormatoValido } from "@/constants/formatos.constant";
import type { FormatoId } from "@/core/shared/domain/view/adaptation.view";
import { RutaEnum } from "@/enums/ruta.enum";
import useCmpGuia from "@/composables/business/cmp-guia/cmp-guia.composable";

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

    // El tema elegido en la guía (?tema=N lo conserva al recargar): la IA solo lee ese tema.
    const { temaAbierto } = useCmpGuia();
    const temaId = computed(() => {
      const enUrl = Number(route.query.tema);
      if (Number.isInteger(enUrl) && enUrl > 0) return `tema-${enUrl}`;
      return temaAbierto.value ?? "tema-1";
    });

    return { RutaEnum, PREFIX, reintentos, formato, temaId };
  },
});
